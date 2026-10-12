/* P2.1c — local-only IndexedDB repository for CONFIRMED user strokes.
 * No network/cloud, no device identity, no automatic grading. Every record
 * is keyed to the exact published PDF and the glyph's frozen source SHA.
 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(root)root.ZitiePracticeLocalStore=api;
})(typeof window!=='undefined'?window:null,function(){
  'use strict';
  const DB='zitie-guided-practice-v1';
  const STORE='sessions';
  const SHA=/^[a-f0-9]{64}$/;
  function makeKey({glyphId,pdfHash,sourceHash}={}){
    if(!Number.isInteger(glyphId)||glyphId<1||glyphId>201||
       !SHA.test(pdfHash||'')||!SHA.test(sourceHash||''))
      throw Error('Invalid source-locked practice storage key');
    return pdfHash+':'+glyphId+':'+sourceHash;
  }
  function requestAsPromise(request){
    return new Promise((yes,no)=>{
      request.onsuccess=()=>yes(request.result);
      request.onerror=()=>no(request.error||Error('IndexedDB request failed'));
    });
  }
  class LocalPracticeStore{
    constructor({dbName=DB,indexedDBFactory=null}={}){
      this.dbName=dbName;
      this.factory=indexedDBFactory||
        (typeof indexedDB==='undefined'?null:indexedDB);
      this.dbPromise=null;
      this.queue=Promise.resolve();
    }
    async db(){
      if(!this.factory)throw Error('IndexedDB unavailable in this browser');
      if(!this.dbPromise){
        this.dbPromise=new Promise((yes,no)=>{
          let request;
          try{request=this.factory.open(this.dbName,1);}
          catch(error){no(error);return;}
          request.onupgradeneeded=()=>{
            const db=request.result;
            if(!db.objectStoreNames.contains(STORE))
              db.createObjectStore(STORE,{keyPath:'key'});
          };
          request.onerror=()=>no(request.error||Error('IndexedDB opening failed'));
          request.onblocked=()=>no(Error('IndexedDB upgrade blocked'));
          request.onsuccess=()=>{
            const db=request.result;
            db.onversionchange=()=>{db.close();this.dbPromise=null;};
            yes(db);
          };
        }).catch(error=>{this.dbPromise=null;throw error;});
      }
      return this.dbPromise;
    }
    // Serialize writes and deletes within this tab, so a slower earlier
    // acceptance never overwrites a newer undo/restart snapshot.
    enqueue(callback){
      const result=this.queue.catch(()=>{}).then(callback);
      this.queue=result;
      return result;
    }
    flush(){return this.queue;}
    async load(identity){
      const key=makeKey(identity);
      // A load cannot race a queued save/clear from an earlier practice.
      await this.queue.catch(()=>{});
      const db=await this.db();
      const tx=db.transaction(STORE,'readonly');
      const row=await requestAsPromise(tx.objectStore(STORE).get(key));
      return row?.snapshot||null;
    }
    save(snapshot){
      const key=makeKey(snapshot);
      if(!snapshot||snapshot.schemaVersion!==1||
         !Number.isSafeInteger(snapshot.revision)||
         !Array.isArray(snapshot.accepted))
        return Promise.reject(Error('Refuse to save unversioned practice data'));
      const immutable=JSON.parse(JSON.stringify(snapshot));
      return this.enqueue(async()=>{
        const db=await this.db();
        return new Promise((yes,no)=>{
          const tx=db.transaction(STORE,'readwrite');
          const store=tx.objectStore(STORE);
          let error=null;
          const lookup=store.get(key);
          lookup.onsuccess=()=>{
            const old=lookup.result?.snapshot;
            if(old&&old.revision>immutable.revision){
              error=Error('Stale practice revision; reload before overwriting');
              tx.abort();return;
            }
            store.put({key,updatedAt:Date.now(),snapshot:immutable});
          };
          lookup.onerror=()=>{error=lookup.error;tx.abort();};
          tx.oncomplete=()=>yes({saved:true,revision:immutable.revision});
          tx.onerror=()=>no(error||tx.error||Error('Practice save failed'));
          tx.onabort=()=>no(error||tx.error||Error('Practice save aborted'));
        });
      });
    }
    remove(identity){
      const key=makeKey(identity);
      return this.enqueue(async()=>{
        const db=await this.db();
        return new Promise((yes,no)=>{
          const tx=db.transaction(STORE,'readwrite');
          tx.objectStore(STORE).delete(key);
          tx.oncomplete=()=>yes({deleted:true});
          tx.onerror=()=>no(tx.error||Error('Practice deletion failed'));
          tx.onabort=()=>no(tx.error||Error('Practice deletion aborted'));
        });
      });
    }
  }
  return {LocalPracticeStore,makeKey,DB,STORE};
});
