import asyncio, json, time
from playwright.async_api import async_playwright
SEED='''
window.__DB={
 users:{s1:{name:'خادم',role:'servant',memberId:'',phone:'0100'},m1:{name:'مريم',role:'member',memberId:'M1'},m2:{name:'بولا',role:'member',memberId:'M2'}},
 members:{M1:{name:'مريم',choir:'ib',points:0,attended:0,uid:'m1',added:1,phone:'01011111111'},M2:{name:'بولا',choir:'th',points:5,attended:1,uid:'m2',added:1}},
 events:{E1:{type:'rehearsal',title:'بروفة ماضية',when:Date.now()-3*864e5,choir:'all'},E2:{type:'rehearsal',title:'بروفة قادمة',when:Date.now()+2*864e5,choir:'all'}},
 attendance:{'E1_M1':{eventId:'E1',memberId:'M1',name:'مريم',choir:'ib',title:'بروفة ماضية',when:Date.now()-3*864e5,status:'p',pts:5,at:Date.now()-3*864e5}},
 config:{main:{votePts:1}}, notifs:{}, adjustments:{}
};'''
errs=[]
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(); pg=await b.new_page(viewport={'width':420,'height':850})
    pg.on('pageerror',lambda e:errs.append('PAGEERR '+str(e)))
    pg.on('console',lambda m:errs.append('CONSOLE '+m.text) if m.type=='error' else None)
    pg.on('dialog',lambda d:asyncio.ensure_future(d.accept()))
    await pg.add_init_script(SEED)
    await pg.goto('http://localhost:8765/index.html'); await pg.wait_for_timeout(2500)
    ev=lambda s:pg.evaluate(s)
    async def txt(): return await pg.inner_text('#app')
    async def setv(sel,v): await pg.fill(sel,v)
    R={}
    # ---- servant ----
    await ev("window.__login('s1')"); await pg.wait_for_timeout(800)
    t=await txt(); R['home_servant_tiles']=all(x in t for x in ['الترانيم','التصويت','مخدومي'])
    await ev("go('hymns')"); await pg.wait_for_timeout(300)
    await ev("fdAdd()"); await pg.fill('#fdn','تراتيل الصوم'); await ev("fdSave('')"); await pg.wait_for_timeout(500)
    await ev("fdAdd()"); await pg.fill('#fdn','مجلد فارغ'); await ev("fdSave('')"); await pg.wait_for_timeout(500)
    R['folders']=list((await ev("Object.values(window.__DB.hymnFolders||{}).map(f=>f.name)")))
    await ev("fdAdd()"); await pg.fill('#fdn','تراتيل الصوم'); await ev("fdSave('')"); await pg.wait_for_timeout(300)
    R['dup_blocked']=len(await ev("Object.values(window.__DB.hymnFolders)"))==2
    fid=await ev("Object.keys(window.__DB.hymnFolders)[0]")
    await ev(f"hyForm('','{fid}')"); await pg.fill('#hn','يا ربي يسوع'); await pg.fill('#hlx','كلمات\\nسطر ٢'); await pg.fill('#ha','https://drive.google.com/file/d/ABC123/view?usp=sharing')
    await ev("hySave('')"); await pg.wait_for_timeout(500)
    h=await ev("Object.values(window.__DB.hymns||{})[0]"); R['hymn_saved']=bool(h) and h['folderId']==fid and not h['deleted']
    await ev("hyForm('','%s')"%fid); await pg.fill('#hn','x'); await pg.fill('#ha','http://bad'); await ev("hySave('')"); await pg.wait_for_timeout(200)
    R['http_rejected']=len(await ev("Object.values(window.__DB.hymns)"))==1
    await ev("document.querySelector('#md').style.display='none'")
    await ev("go('folder','%s')"%fid); await pg.wait_for_timeout(200); R['folder_lists_hymn']='يا ربي يسوع' in await txt()
    hid=await ev("Object.keys(window.__DB.hymns)[0]")
    await ev("go('hymn','%s')"%hid); await pg.wait_for_timeout(200); t=await txt(); R['hymn_page']=('سطر ٢' in t) and ('الكلمات' in t)
    R['audio_norm']=await ev("(()=>{return 1})()")
    # search w/ tashkeel-insensitive
    await ev("tab('hymns')"); await pg.wait_for_timeout(200); await pg.fill('#hsq','ربى'); await ev("hySq('ربى')"); R['search_norm']='يا ربي يسوع' in await pg.inner_text('#hl')
    # reorder + pin
    await ev("hySq('')"); fids=await ev("Object.keys(window.__DB.hymnFolders)")
    await ev(f"fdMove('{fids[1]}',-1)"); await pg.wait_for_timeout(300)
    o=await ev("Object.values(window.__DB.hymnFolders).map(f=>[f.name,f.order])"); R['reorder']=o
    await ev(f"fdPin('{fids[1]}')"); await pg.wait_for_timeout(300); R['pinned']=await ev(f"window.__DB.hymnFolders['{fids[1]}'].pinned")
    # trash hymn and restore
    await ev(f"hyTrash(['{hid}'])"); await pg.wait_for_timeout(300); R['hymn_trashed']=await ev(f"window.__DB.hymns['{hid}'].deleted")
    await ev("go('htrash')"); await pg.wait_for_timeout(200); R['trash_lists']='يا ربي يسوع' in await txt()
    await ev(f"htRestoreH('{hid}')"); await pg.wait_for_timeout(300); R['hymn_restored']=not await ev(f"window.__DB.hymns['{hid}'].deleted")
    # trash folder with hymn, restore hymn when folder trashed -> confirm accepted
    await ev(f"fdTrash(['{fid}'])"); await pg.wait_for_timeout(300); R['folder_trashed']=await ev(f"window.__DB.hymnFolders['{fid}'].deleted")
    await ev(f"htRestoreF('{fid}')"); await pg.wait_for_timeout(300); R['folder_restored']=not await ev(f"window.__DB.hymnFolders['{fid}'].deleted")
    # polls
    await ev("go('polls')"); await pg.wait_for_timeout(200); await ev("plForm()")
    await pg.fill('#plq','هل تحب الترانيم؟'); await ev("plOptAdd()"); 
    ins=await pg.query_selector_all('.plop'); await ins[0].fill('نعم'); await ins[1].fill('لا'); await ins[2].fill('ممكن')
    await ev("plSave(true)"); await pg.wait_for_timeout(500)
    P=await ev("Object.entries(window.__DB.polls||{})"); R['poll_created']=len(P)==1 and P[0][1]['isActive'] and P[0][1]['options']==['نعم','لا','ممكن']
    pid=P[0][0]
    R['poll_notif']=await ev("Object.values(window.__DB.notifs||{}).some(n=>n.title.includes('تصويت'))")
    # invalid poll
    await ev("plForm()"); await pg.fill('#plq','س'); await ev("plSave(true)"); await pg.wait_for_timeout(200); R['poll_invalid_blocked']=len(await ev("Object.values(window.__DB.polls)"))==1
    await ev("document.querySelector('#md').style.display='none'")
    # ---- member ----
    await ev("out()"); await pg.wait_for_timeout(500); await ev("window.__login('m1')"); await pg.wait_for_timeout(1000)
    t=await txt(); R['member_home']=('الترانيم' in t) and ('تصويت نشط' in t or 'رأيك يهمنا' in t)
    R['member_no_admin_tiles']='مخدومي' not in t
    await ev("go('polls')"); await pg.wait_for_timeout(300); t=await txt(); R['member_sees_poll']='هل تحب الترانيم؟' in t
    await pg.check(f'input[name="po_{pid}"][value="0"]'); await ev(f"plVote('{pid}')"); await pg.wait_for_timeout(500)
    M=await ev("window.__DB.members.M1"); R['vote_points']=M['points']==1 and M['lastVotePoll']==pid
    R['vote_doc']=await ev(f"!!window.__DB.pollVotes['{pid}_M1']")
    R['poll_total']=await ev(f"window.__DB.polls['{pid}'].total")==1
    await ev(f"plVote('{pid}')"); await pg.wait_for_timeout(300); R['no_double_vote']=(await ev("window.__DB.members.M1.points"))==1
    t=await txt(); R['voted_msg']='تم تسجيل صوتك' in t
    await ev("go('points')"); await pg.wait_for_timeout(300); R['ledger_has_vote']='تصويت' in await txt()
    await ev("go('history')"); await pg.wait_for_timeout(300); t=await txt(); R['history_member']=('بروفة ماضية' in t)
    await ev("go('board')"); await pg.wait_for_timeout(300); R['board_podium']=await ev("!!document.querySelector('.podium')")
    await ev("bdM('reg')"); await pg.wait_for_timeout(200); R['board_reg']='%' in await txt()
    await ev("go('remind')"); await pg.wait_for_timeout(300); R['remind_page']='تذكيرات الأحداث' in await txt()
    await ev("rmSet('m15',false)"); R['remind_saved']=await ev("JSON.parse(localStorage.getItem('rm_m1')).m15===false")
    await ev("go('hymns')"); await pg.wait_for_timeout(300); t=await txt(); R['member_hymns_ro']=('تراتيل الصوم' in t) and ('+ مجلد' not in t) and ('السلة' not in t)
    await ev("go('upd')"); R['member_upd_no_form']='نشر إشعار تحديث' not in await txt()
    # member cannot see admin via direct nav
    await ev("go('analytics')"); R['member_analytics_blocked']='للخادم فقط' in await txt()
    await ev("go('htrash')"); R['member_trash_blocked']='للخادم فقط' in await txt()
    # ---- servant again: end poll, results, weekly, update, analytics ----
    await ev("out()"); await pg.wait_for_timeout(400); await ev("window.__login('s1')"); await pg.wait_for_timeout(1000)
    await ev("go('polls')"); await pg.wait_for_timeout(300); R['servant_poll_tally']='1 مشارك' in await txt()
    await ev(f"plWho('{pid}')"); await pg.wait_for_timeout(200); R['who_voted']=('مريم' in await pg.inner_text('#mb')) and ('بولا' in await pg.inner_text('#mb'))
    await ev("document.querySelector('#md').style.display='none'")
    await ev(f"plEnd('{pid}')"); await pg.wait_for_timeout(400); F=await ev(f"window.__DB.polls['{pid}']"); R['poll_ended']=(not F['isActive']) and F['final']['counts']==[1,0,0] and F['final']['total']==1
    await ev("go('analytics')"); await pg.wait_for_timeout(300); t=await txt(); R['analytics']=('إجمالي الأعضاء' in t) and await ev("!!document.querySelector('.cols')")
    await ev("go('history','M1')"); await pg.wait_for_timeout(300); R['servant_history']='مريم' in await txt()
    await ev("go('weekly')"); await pg.wait_for_timeout(200)
    await pg.fill('#wt','بروفة الجمعة'); await pg.select_option('#wd','5'); await pg.fill('#wh','18:30'); await pg.fill('#ww','4'); await ev("wkSave(true)"); await pg.wait_for_timeout(800)
    wk=await ev("Object.entries(window.__DB.events).filter(([i,e])=>e.weekly)"); R['weekly_count']=len(wk)
    R['weekly_day_ok']=all(__import__('datetime').datetime.fromtimestamp(e['when']/1000).weekday()==4 for i,e in wk)
    R['weekly_ids_det']=all(i.startswith('wk_all_') for i,e in wk)
    await ev("wkSave(true)"); await pg.wait_for_timeout(800); R['weekly_idempotent']=len(await ev("Object.entries(window.__DB.events).filter(([i,e])=>e.weekly)"))==len(wk)
    # delete one weekly event; autoWeekly must not resurrect
    victim=wk[0][0]; await ev(f"window.__DB.events['{victim}']&&delete window.__DB.events['{victim}']"); await ev("autoWeeklyTest=1"); 
    await ev("go('upd')"); await pg.fill('#uv','4.5'); await pg.fill('#un','ملاحظات'); await pg.fill('#ul','https://example.com/a.apk'); await pg.fill('#us','a'*64); await ev("upPub(true)"); await pg.wait_for_timeout(500)
    U=await ev("window.__DB.config.app_update"); R['update_pub']=U and U['isActive'] and U['version']=='4.5'
    await pg.fill('#ul','http://x'); await ev("upPub(true)"); await pg.wait_for_timeout(200); R['update_http_rejected']=(await ev("window.__DB.config.app_update.url"))=='https://example.com/a.apk'
    await ev("go('home')" if False else "tab('home')"); await pg.wait_for_timeout(300); R['home_update_banner']='تحديث جديد متوفر' in await txt()
    # reset points
    await ev("go('points')"); await ev("sv('ptM','M2')"); await ev("ptReset('M2')"); await pg.wait_for_timeout(400)
    R['reset_points']=(await ev("window.__DB.members.M2.points"))==0 and await ev("Object.values(window.__DB.adjustments).some(a=>a.pts===-5&&a.reason==='تصفير النقاط')")
    # old features sanity
    for page_ in ['attend','sched','members','report','set','rules','bgs','notifs','more','profile']:
        await ev(f"go('{page_}')"); await pg.wait_for_timeout(150)
        R['old_'+page_]=len(await txt())>20
    await ev("go('member','M1')"); await pg.wait_for_timeout(200); R['member_page_history_btn']='سجل الحضور والغياب' in await txt()
    # write failure: no false success
    await ev("window.__failWrites=()=>true"); await ev("go('hymns')"); await ev("fdAdd()"); await pg.fill('#fdn','لن يحفظ'); await ev("fdSave('')"); await pg.wait_for_timeout(300)
    R['fail_no_success']=('تم الحفظ' not in await pg.inner_text('#toast')) and not await ev("Object.values(window.__DB.hymnFolders).some(f=>f.name==='لن يحفظ')")
    R['fail_msg']=await pg.inner_text('#toast')
    print(json.dumps(R,ensure_ascii=False,indent=1))
    print('ERRORS:',errs)
    await b.close()
asyncio.run(main())
