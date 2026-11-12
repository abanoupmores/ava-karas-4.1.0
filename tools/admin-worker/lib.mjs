// منطق تنفيذ الطلبات الإدارية (بدون استيراد firebase-admin) — يُحقن db/auth لتسهيل الاختبار.
export const DEFAULT_PW='123456';
export const PROJECT_ID='youth-family-c039e';
// نفس دوال التطبيق (src/main.js) لتحويل رقم الهاتف إلى بريد الدخول
export const norm=v=>String(v||'').replace(/[٠-٩]/g,c=>'٠١٢٣٤٥٦٧٨٩'.indexOf(c)).replace(/\D/g,'').slice(-10);
export const phoneMail=v=>{const d=norm(v);return d.length>=10?'0'+d+'@phone.choir.app':''};
const failed=message=>({status:'failed',message});
const done=message=>({status:'done',message});

// r = مستند adminRequests. يرجع {status,message}. لا يكتب كلمات مرور في Firestore.
export async function handle(r,{db,auth}){
  if(!r||!['resetPassword','changePhone'].includes(r.type))return failed('نوع طلب غير معروف');
  if(typeof r.targetUid!=='string'||!r.targetUid||typeof r.requestedBy!=='string'||!r.requestedBy)return failed('بيانات الطلب ناقصة');
  const req=await db.doc('users/'+r.requestedBy).get();
  const byServant=req.exists&&req.data().role==='servant';
  const selfPhone=r.type==='changePhone'&&r.targetUid===r.requestedBy;
  if(!byServant&&!selfPhone)return failed('صاحب الطلب غير مخوّل');
  const tu=await db.doc('users/'+r.targetUid).get();
  if(!tu.exists)return failed('حساب الهدف غير موجود');

  if(r.type==='resetPassword'){
    if(tu.data().role!=='member')return failed('إعادة التعيين للمخدومين فقط');
    const m=await db.doc('members/'+(r.memberId||'_')).get();
    if(!m.exists||m.data().uid!==r.targetUid||tu.data().memberId!==r.memberId)return failed('الحساب غير مربوط بهذا المخدوم');
    await auth.updateUser(r.targetUid,{password:DEFAULT_PW});
    await auth.revokeRefreshTokens(r.targetUid);
    await db.doc('users/'+r.targetUid).update({mustChangePw:true});
    return done('الباسورد أصبح '+DEFAULT_PW+' وسيُطلب منه تغييره عند الدخول');
  }

  // changePhone
  const p=norm(r.newPhone);
  if(p.length<10)return failed('رقم الهاتف غير صالح');
  const user=await auth.getUser(r.targetUid);
  if(!String(user.email||'').endsWith('@phone.choir.app'))return {status:'skipped',message:'الحساب يسجّل الدخول بإيميل حقيقي؛ لم يتغير اسم الدخول'};
  const mail=phoneMail(p);
  if(mail===user.email)return done('رقم الدخول لم يتغير');
  try{const o=await auth.getUserByEmail(mail);if(o.uid!==r.targetUid)return failed('الرقم مستخدم في حساب آخر')}
  catch(e){if(!e||e.code!=='auth/user-not-found')throw e}
  await auth.updateUser(r.targetUid,{email:mail});
  await db.doc('users/'+r.targetUid).update({contact:p});
  return done('تم تحديث رقم الدخول');
}
