// اختبار منطق المهمة الإدارية بقاعدة وهمية في الذاكرة: node tests/admin-worker.test.mjs
import {handle,norm,phoneMail,DEFAULT_PW} from '../tools/admin-worker/lib.mjs';
let ok=true;const t=(n,a,b)=>{const g=JSON.stringify(a)===JSON.stringify(b);if(!g)ok=false;console.log(g?'PASS':'FAIL',n,g?'':'got '+JSON.stringify(a)+' expected '+JSON.stringify(b))};
function env(){
  const D={'users/S1':{role:'servant',name:'خادم'},'users/U1':{role:'member',memberId:'M1',phone:'1012345678'},'users/U2':{role:'member',memberId:'M2'},
    'members/M1':{uid:'U1'},'members/M2':{uid:'U2'}};
  const calls=[];
  const A={U1:{uid:'U1',email:'01012345678@phone.choir.app'},U2:{uid:'U2',email:'01099999999@phone.choir.app'},U3:{uid:'U3',email:'real@gmail.com'}};
  D['users/U3']={role:'member',memberId:'M3'};
  const db={doc:p=>({get:async()=>({exists:p in D,data:()=>D[p],ref:null}),update:async x=>{calls.push(['upd',p,x]);D[p]={...D[p],...x}}})};
  const auth={updateUser:async(u,x)=>{calls.push(['auth',u,x]);Object.assign(A[u],x.email?{email:x.email}:{})},revokeRefreshTokens:async u=>calls.push(['revoke',u]),
    getUser:async u=>A[u],getUserByEmail:async e=>{const f=Object.values(A).find(x=>x.email===e);if(!f)throw{code:'auth/user-not-found'};return f}};
  return {db,auth,calls,D};
}
t('norm',[norm('٠١٠١٢٣٤٥٦٧٨'),norm('+20 101 234 5678')],['1012345678','1012345678']);
t('phoneMail',phoneMail('01012345678'),'01012345678@phone.choir.app');
t('phoneMail قصير',phoneMail('123'),'');
let e=env();
t('reset: خادم',(await handle({type:'resetPassword',targetUid:'U1',memberId:'M1',requestedBy:'S1'},e)).status,'done');
t('reset: كلمة المرور الافتراضية + revoke + mustChangePw',[e.calls.some(c=>c[0]==='auth'&&c[2].password===DEFAULT_PW),e.calls.some(c=>c[0]==='revoke'),e.D['users/U1'].mustChangePw],[true,true,true]);
e=env();t('reset: مخدوم يطلب لنفسه مرفوض',(await handle({type:'resetPassword',targetUid:'U1',memberId:'M1',requestedBy:'U1'},e)).status,'failed');
t('reset: لا تغيير تم',e.calls.length,0);
e=env();t('reset: memberId لا يطابق',(await handle({type:'resetPassword',targetUid:'U1',memberId:'M2',requestedBy:'S1'},e)).status,'failed');
e=env();t('reset: هدف غير موجود',(await handle({type:'resetPassword',targetUid:'NOPE',memberId:'M1',requestedBy:'S1'},e)).status,'failed');
e=env();t('reset: حساب خادم مرفوض',(await handle({type:'resetPassword',targetUid:'S1',memberId:'',requestedBy:'S1'},e)).status,'failed');
e=env();t('phone: خادم يغيّر لمخدوم',(await handle({type:'changePhone',targetUid:'U1',memberId:'M1',newPhone:'01111111111',requestedBy:'S1'},e)).status,'done');
t('phone: الإيميل الجديد',e.calls.find(c=>c[0]==='auth')[2].email,'01111111111@phone.choir.app');
e=env();t('phone: رقم مستخدم عند حساب آخر',(await handle({type:'changePhone',targetUid:'U1',memberId:'M1',newPhone:'01099999999',requestedBy:'S1'},e)).status,'failed');
t('phone: لا تغيير تم',e.calls.length,0);
e=env();t('phone: ذاتي لنفسه مسموح',(await handle({type:'changePhone',targetUid:'U1',memberId:'',newPhone:'01122222222',requestedBy:'U1'},e)).status,'done');
e=env();t('phone: مخدوم لغيره مرفوض',(await handle({type:'changePhone',targetUid:'U2',memberId:'',newPhone:'01122222222',requestedBy:'U1'},e)).status,'failed');
e=env();t('phone: حساب بإيميل حقيقي skipped',(await handle({type:'changePhone',targetUid:'U3',memberId:'M3',newPhone:'01122222222',requestedBy:'S1'},e)).status,'skipped');
e=env();t('phone: رقم قصير',(await handle({type:'changePhone',targetUid:'U1',memberId:'M1',newPhone:'123',requestedBy:'S1'},e)).status,'failed');
e=env();t('phone: نفس الرقم',(await handle({type:'changePhone',targetUid:'U1',memberId:'M1',newPhone:'01012345678',requestedBy:'S1'},e)).status,'done');
e=env();t('نوع مجهول',(await handle({type:'deleteEverything',targetUid:'U1',requestedBy:'S1'},e)).status,'failed');
process.exit(ok?0:1);
