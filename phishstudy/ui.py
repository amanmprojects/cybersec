"""Shared HTML components and the design system.

The application renders server-side HTML with no template engine and no
front-end build step, so all styles and components live here.
"""
from __future__ import annotations

import html

CSS = """
*,*::before,*::after{box-sizing:border-box}
:root{
 --bg:#f4f6fb;--surface:#fff;--surface2:#fafbfe;--line:#e6eaf2;--line2:#eef1f7;
 --ink:#0d1424;--ink2:#48566b;--muted:#8592a8;
 --brand:#4f46e5;--brand2:#6366f1;--brandsoft:#eef0ff;
 --ok:#059669;--oksoft:#e7f7f1;--warn:#d97706;--warnsoft:#fdf3e4;
 --bad:#dc2626;--badsoft:#fdecec;--info:#2563eb;--infosoft:#e8f0fe;
 --r:14px;--rs:10px;
 --sh:0 1px 2px rgba(16,24,40,.04),0 4px 14px rgba(16,24,40,.05);
 --sh2:0 2px 6px rgba(16,24,40,.06),0 12px 32px rgba(16,24,40,.07);
 --sbw:238px;
}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);
 font-family:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Inter,"Helvetica Neue",Arial,sans-serif;
 font-size:14px;line-height:1.55;-webkit-font-smoothing:antialiased}
h1,h2,h3,h4{margin:0;line-height:1.2;letter-spacing:-.02em;font-weight:650}
p{margin:0 0 10px}
a{color:var(--brand);text-decoration:none}
a:hover{text-decoration:underline}
small{font-size:12px}
.mono{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace}
.simbar{background:linear-gradient(90deg,#fde68a,#fcd34d);color:#4a3200;font-size:12px;
 font-weight:650;letter-spacing:.02em;padding:7px 20px;text-align:center;border-bottom:1px solid #eab308}
.simbar span{opacity:.78;font-weight:550}

/* ---------------- admin shell ---------------- */
.shell{display:flex;min-height:calc(100vh - 31px)}
.sb{width:var(--sbw);flex:none;background:#0d1424;color:#cfd7e6;padding:18px 14px;
 position:sticky;top:31px;height:calc(100vh - 31px);overflow:auto;display:flex;flex-direction:column;gap:6px}
.sb .brand{display:flex;align-items:center;gap:10px;color:#fff;font-weight:700;font-size:16px;
 padding:2px 8px 18px;letter-spacing:-.02em}
.sb .brand:hover{text-decoration:none}
.sb .logo{width:30px;height:30px;border-radius:9px;display:grid;place-items:center;
 background:linear-gradient(140deg,#6366f1,#4338ca);box-shadow:0 3px 10px rgba(79,70,229,.45)}
.sb .grp{font-size:10px;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#5f6c84;
 padding:14px 10px 6px}
.sb a.item{display:flex;align-items:center;gap:10px;padding:8px 10px;border-radius:9px;color:#c7d0e0;
 font-size:13.5px;font-weight:550}
.sb a.item:hover{background:rgba(255,255,255,.07);color:#fff;text-decoration:none}
.sb a.item.on{background:rgba(99,102,241,.22);color:#fff;box-shadow:inset 0 0 0 1px rgba(129,140,248,.35)}
.sb a.item .ic{width:18px;text-align:center;opacity:.9}
.sb .whoami{margin-top:auto;border-top:1px solid rgba(255,255,255,.08);padding:14px 8px 4px;
 display:flex;align-items:center;gap:9px;font-size:12.5px}
.sb .whoami .nm{color:#fff;font-weight:600;line-height:1.2}
.sb .whoami .rl{color:#7f8ca3;font-size:11px}
.main{flex:1;min-width:0}
.topbar{background:rgba(255,255,255,.86);backdrop-filter:blur(8px);border-bottom:1px solid var(--line);
 padding:0 26px;height:58px;display:flex;align-items:center;gap:14px;position:sticky;top:31px;z-index:40}
.crumb{font-size:13px;color:var(--muted);display:flex;align-items:center;gap:7px}
.crumb b{color:var(--ink);font-weight:600}
.topact{margin-left:auto;display:flex;gap:8px;align-items:center;flex-wrap:wrap}
.wrap{max-width:1240px;margin:0 auto;padding:24px 26px 60px}
.wrap.narrow{max-width:900px}
@media(max-width:900px){
 .shell{display:block}
 .sb{position:static;width:auto;height:auto;flex-direction:row;flex-wrap:wrap;align-items:center;padding:10px}
 .sb .brand{padding:0 10px 0 0}
 .sb .grp,.sb .whoami{display:none}
 .topbar{position:static}
}

/* ---------------- primitives ---------------- */
.card{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh);padding:20px}
.grid{display:grid;gap:16px}
.g2{grid-template-columns:1fr 1fr}.g3{grid-template-columns:repeat(3,1fr)}.g4{grid-template-columns:repeat(4,1fr)}
@media(max-width:980px){.g2,.g3,.g4{grid-template-columns:1fr}}
.hero{display:flex;gap:20px;align-items:flex-end;justify-content:space-between;margin-bottom:20px;flex-wrap:wrap}
.hero h1{font-size:25px;margin-bottom:6px}
.hero p{color:var(--ink2);margin:0;max-width:64ch;font-size:14px}
.eyebrow{display:inline-flex;align-items:center;gap:7px;font-size:11px;font-weight:700;
 letter-spacing:.1em;text-transform:uppercase;color:var(--brand);margin-bottom:8px}
.eyebrow::before{content:"";width:16px;height:2px;background:var(--brand);border-radius:2px}
.kpi{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);box-shadow:var(--sh);
 padding:16px 18px;position:relative;overflow:hidden}
.kpi::before{content:"";position:absolute;inset:0 auto 0 0;width:3px;background:var(--k,#cbd5e1)}
.kpi .k-lbl{font-size:11.5px;font-weight:650;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}
.kpi .k-val{font-size:29px;font-weight:700;letter-spacing:-.03em;margin:6px 0 2px;line-height:1.05}
.kpi .k-sub{font-size:12.5px;color:var(--ink2)}
.kpi .k-ico{position:absolute;top:14px;right:14px;width:26px;height:26px;border-radius:8px;
 display:grid;place-items:center;background:var(--ksoft,#eef1f7);color:var(--k,#64748b);font-size:13px}
.chip{display:inline-flex;align-items:center;gap:5px;padding:3px 9px;border-radius:999px;
 font-size:11.5px;font-weight:650;border:1px solid transparent;white-space:nowrap}
.chip.ok{background:var(--oksoft);color:#046c50;border-color:#b9e8d5}
.chip.warn{background:var(--warnsoft);color:#a35c07;border-color:#f6dfb8}
.chip.bad{background:var(--badsoft);color:#b11d1d;border-color:#f7c9c9}
.chip.info{background:var(--infosoft);color:#1c4fbd;border-color:#c6d8fb}
.chip.mute{background:#f1f4f9;color:#5b6a80;border-color:#e0e6ef}
.chip.brand{background:var(--brandsoft);color:#4338ca;border-color:#d5d8fb}
.dot{width:6px;height:6px;border-radius:50%;background:currentColor;flex:none}
.btn{display:inline-flex;align-items:center;justify-content:center;gap:7px;
 padding:9px 15px;border-radius:9px;font-size:13.5px;font-weight:600;cursor:pointer;
 border:1px solid transparent;transition:.15s;font-family:inherit;background:none}
.btn:hover{text-decoration:none;transform:translateY(-1px)}
.btn-p{background:var(--brand);color:#fff;box-shadow:0 3px 10px rgba(79,70,229,.3)}
.btn-p:hover{background:#4338ca}
.btn-s{background:var(--surface);color:var(--ink2);border-color:var(--line)}
.btn-s:hover{background:var(--surface2);color:var(--ink)}
.btn-ok{background:var(--ok);color:#fff}
.btn-bad{background:var(--bad);color:#fff}
.btn-xs{padding:5px 10px;font-size:12px;border-radius:7px}
.btn[disabled]{opacity:.5;cursor:not-allowed;transform:none}
label{display:block;font-size:11.5px;font-weight:650;letter-spacing:.05em;text-transform:uppercase;
 color:var(--muted);margin:0 0 6px}
input[type=text],input[type=password],input[type=email],input[type=date],input[type=number],
input:not([type]),select,textarea{
 width:100%;padding:9px 12px;border:1px solid var(--line);border-radius:9px;background:var(--surface);
 color:var(--ink);font-size:14px;font-family:inherit;transition:.15s}
input:focus,select:focus,textarea:focus{outline:0;border-color:var(--brand2);box-shadow:0 0 0 3px rgba(99,102,241,.16)}
textarea{min-height:120px;resize:vertical;line-height:1.55}
.field{margin-bottom:13px}
.field .hint{font-size:11.5px;color:var(--muted);margin-top:4px;text-transform:none;letter-spacing:0;font-weight:400}
.row{display:grid;grid-template-columns:1fr 1fr;gap:12px}
@media(max-width:700px){.row{grid-template-columns:1fr}}
table{width:100%;border-collapse:collapse;font-size:13.5px}
th{font-size:10.5px;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);
 text-align:left;padding:0 10px 9px;border-bottom:1px solid var(--line)}
td{padding:10px;border-bottom:1px solid var(--line2);vertical-align:middle}
tr:last-child td{border-bottom:0}
tbody tr:hover{background:var(--surface2)}
.num{text-align:right;font-variant-numeric:tabular-nums}
.table-wrap{overflow-x:auto}
.av{width:30px;height:30px;border-radius:50%;display:grid;place-items:center;flex:none;
 font-size:11.5px;font-weight:700;color:#fff;letter-spacing:.02em}
.av.lg{width:38px;height:38px;font-size:13.5px}
.who{display:flex;align-items:center;gap:10px}
.who .n{font-weight:600;line-height:1.25}
.who .e{font-size:12px;color:var(--muted);line-height:1.25}
.funnel{display:flex;flex-direction:column;gap:11px}
.fn-row{display:grid;grid-template-columns:82px 1fr 70px;align-items:center;gap:11px}
.fn-lbl{font-size:12.5px;font-weight:600;color:var(--ink2)}
.fn-track{height:9px;background:#eef1f7;border-radius:99px;overflow:hidden}
.fn-fill{height:100%;border-radius:99px;transition:width .4s}
.fn-val{font-size:12.5px;font-weight:700;text-align:right;font-variant-numeric:tabular-nums;color:var(--ink)}
.fn-val em{font-style:normal;font-weight:550;color:var(--muted);font-size:11.5px}
.donutwrap{display:flex;align-items:center;gap:20px;flex-wrap:wrap}
.donut{width:132px;height:132px;flex:none}
.legend{display:flex;flex-direction:column;gap:7px;font-size:12.5px;min-width:150px;flex:1}
.lg{display:flex;align-items:center;gap:8px;color:var(--ink2)}
.lg .sw{width:9px;height:9px;border-radius:3px;flex:none}
.lg b{margin-left:auto;font-variant-numeric:tabular-nums;color:var(--ink)}
.donut-c{font-size:22px;font-weight:700;fill:var(--ink)}
.donut-s{font-size:9px;font-weight:650;fill:var(--muted);letter-spacing:.08em}
.dept{display:flex;flex-direction:column;gap:13px}
.dp{display:grid;grid-template-columns:1fr auto;gap:5px 10px;align-items:baseline}
.dp-n{font-size:13px;font-weight:600}
.dp-v{font-size:12.5px;color:var(--ink2);font-variant-numeric:tabular-nums}
.dp-track{grid-column:1/-1;height:7px;background:#eef1f7;border-radius:99px;overflow:hidden}
.dp-fill{height:100%;border-radius:99px}
.steps{display:grid;grid-template-columns:repeat(4,1fr);gap:14px}
@media(max-width:980px){.steps{grid-template-columns:1fr}}
.step{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);
 padding:15px 16px;box-shadow:var(--sh);position:relative}
.step .n{width:24px;height:24px;border-radius:7px;background:var(--brandsoft);color:var(--brand);
 display:grid;place-items:center;font-size:12px;font-weight:800;margin-bottom:9px}
.step b{display:block;font-size:13.5px;margin-bottom:3px}
.step p{margin:0;font-size:12.5px;color:var(--ink2);line-height:1.5}
.chead{display:flex;align-items:flex-start;gap:14px;justify-content:space-between;
 padding-bottom:14px;margin-bottom:16px;border-bottom:1px solid var(--line2);flex-wrap:wrap}
.chead h3{font-size:16.5px;display:flex;align-items:center;gap:9px;flex-wrap:wrap}
.chead .sub{font-size:12.5px;color:var(--muted);margin-top:4px}
.ctag{display:flex;gap:8px;flex-wrap:wrap;margin-top:9px}
.strip{display:grid;grid-template-columns:repeat(5,1fr);gap:1px;background:var(--line2);
 border:1px solid var(--line2);border-radius:var(--rs);overflow:hidden;margin-bottom:16px}
@media(max-width:760px){.strip{grid-template-columns:repeat(2,1fr)}}
.strip > div{background:var(--surface2);padding:11px 13px}
.strip .sl{font-size:10.5px;font-weight:650;letter-spacing:.07em;text-transform:uppercase;color:var(--muted)}
.strip .sv{font-size:19px;font-weight:700;letter-spacing:-.02em;margin-top:2px;font-variant-numeric:tabular-nums}
.side-h{padding:12px 15px;border-bottom:1px solid var(--line2);font-size:11px;font-weight:700;
 letter-spacing:.08em;text-transform:uppercase;color:var(--muted)}
.tiny{font-size:11.5px;color:var(--muted)}
.note{background:var(--brandsoft);border:1px solid #d9dcfb;border-radius:var(--r);
 padding:15px 17px;font-size:13.5px;color:#3b3486;line-height:1.65}
.note b{color:#312e81}
.note.warn{background:var(--warnsoft);border-color:#f6dfb8;color:#8a4b06}
.note.warn b{color:#78350f}
.note.bad{background:var(--badsoft);border-color:#f7c9c9;color:#991b1b}
.note.bad b{color:#7f1d1d}
.note.ok{background:var(--oksoft);border-color:#b9e8d5;color:#065f46}
.note.ok b{color:#064e3b}
.toolbar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin-bottom:14px}
.toolbar .spacer{margin-left:auto}
.tabs{display:flex;gap:4px;border-bottom:1px solid var(--line);margin-bottom:16px;flex-wrap:wrap}
.tabs a{padding:8px 13px;font-size:13px;font-weight:600;color:var(--ink2);border-bottom:2px solid transparent;margin-bottom:-1px}
.tabs a:hover{color:var(--ink);text-decoration:none}
.tabs a.on{color:var(--brand);border-bottom-color:var(--brand)}
.riskbar{display:flex;align-items:center;gap:9px;min-width:130px}
.riskbar .t{flex:1;height:6px;background:#eef1f7;border-radius:99px;overflow:hidden}
.riskbar .f{height:100%;border-radius:99px}
.risk-low{color:#047857}.risk-moderate{color:#a35c07}.risk-high{color:#b45309}.risk-critical{color:#b11d1d}
.badge-risk{font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px}
.badge-risk.Low{background:var(--oksoft);color:#047857}
.badge-risk.Moderate{background:var(--warnsoft);color:#a35c07}
.badge-risk.High{background:#ffedd5;color:#b45309}
.badge-risk.Critical{background:var(--badsoft);color:#b11d1d}
.spark{display:block;width:100%;height:56px}
.empty{text-align:center;padding:38px 20px;color:var(--muted)}
.empty .ic{font-size:30px;margin-bottom:8px;opacity:.7}
.empty b{display:block;color:var(--ink);font-size:15px;margin-bottom:4px}
.kv{display:grid;grid-template-columns:150px 1fr;gap:6px 14px;font-size:13.5px}
.kv dt{color:var(--muted);font-weight:600}
.kv dd{margin:0}
.foot{margin-top:34px;padding-top:18px;border-top:1px solid var(--line);
 display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font-size:12.5px;color:var(--muted)}
.login-stage{min-height:100vh;display:grid;place-items:center;padding:34px 20px;
 background:radial-gradient(900px 460px at 50% -8%,#e8ecff,transparent),var(--bg)}
.login-card{width:100%;max-width:420px;background:#fff;border:1px solid var(--line);
 border-radius:16px;box-shadow:0 4px 14px rgba(16,24,40,.05),0 22px 52px rgba(16,24,40,.11);overflow:hidden}
.lh{padding:30px 32px 6px;text-align:center}
.lh .lg2{width:46px;height:46px;border-radius:13px;margin:0 auto 13px;display:grid;place-items:center;
 color:#fff;font-weight:800;font-size:17px;background:linear-gradient(140deg,#6366f1,#4338ca);
 box-shadow:0 6px 16px rgba(79,70,229,.32)}
.lh h2{font-size:19px;margin-bottom:5px}
.lh p{font-size:13px;color:var(--muted);margin:0}
.lf{padding:20px 32px 26px}
.lf input{margin-bottom:11px}
.lf .btn{width:100%;padding:11px;font-size:14.5px;margin-top:4px}
.lfoot{padding:14px 32px;background:#f8fafc;border-top:1px solid var(--line2);
 font-size:12px;color:var(--muted);line-height:1.6}
.participant{min-height:100vh}
.mwin{max-width:800px;margin:0 auto;background:var(--surface);border:1px solid var(--line);
 border-radius:var(--r);box-shadow:var(--sh2);overflow:hidden}
.mbar{background:#0d1424;color:#e7ecf4;padding:9px 16px;font-size:12px;display:flex;
 align-items:center;gap:9px;font-weight:600}
.mbar .traffic{display:flex;gap:5px;margin-right:4px}
.mbar .traffic i{width:9px;height:9px;border-radius:50%;display:block}
.mhdr{display:flex;gap:14px;padding:18px 22px 16px;border-bottom:1px solid var(--line2)}
.mhdr .sj{font-size:17px;font-weight:680;letter-spacing:-.01em;margin-bottom:9px;line-height:1.3}
.mfield{font-size:13px;color:var(--ink2);margin-bottom:3px}
.mfield b{color:var(--muted);font-weight:600;font-size:11.5px;text-transform:uppercase;
 letter-spacing:.06em;margin-right:6px}
.mbody{padding:24px 26px;font-size:15px;line-height:1.72;color:#1c2434}
.mbody p{margin:0 0 15px}
.mbody a.fakelink{display:inline-flex;align-items:center;gap:8px;background:#2563eb;color:#fff;
 padding:12px 22px;border-radius:9px;font-weight:600;font-size:14.5px;margin:6px 0 10px;
 box-shadow:0 4px 14px rgba(37,99,235,.3)}
.mbody a.fakelink:hover{background:#1d4ed8;text-decoration:none;transform:translateY(-1px)}
.mfoot{padding:16px 22px;background:var(--surface2);border-top:1px solid var(--line2);
 display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.urlpeek{font-size:11.5px;color:var(--muted);margin-top:2px}
.warnbox{background:#fffbeb;border:1px solid #fde68a;border-radius:var(--rs);padding:12px 15px;
 font-size:13px;color:#78350f;margin:18px 0}
details.spoiler{border:1px dashed #cbd5e1;border-radius:var(--rs);padding:0;margin:18px 0;background:var(--surface2)}
details.spoiler summary{cursor:pointer;padding:11px 15px;font-size:13px;font-weight:650;color:var(--ink2);
 list-style:none;user-select:none}
details.spoiler summary::-webkit-details-marker{display:none}
details.spoiler summary::before{content:"▸ ";color:var(--brand);font-weight:800}
details.spoiler[open] summary::before{content:"▾ "}
details.spoiler .in{padding:0 15px 14px;font-size:13.5px;line-height:1.7;color:var(--ink2)}
details.spoiler ul{margin:8px 0 0;padding-left:20px}
details.spoiler li{margin-bottom:5px}
.inbox{display:grid;grid-template-columns:262px 1fr;gap:16px}
@media(max-width:900px){.inbox{grid-template-columns:1fr}}
.side{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);
 box-shadow:var(--sh);overflow:hidden;align-self:start}
.pick{display:flex;align-items:center;gap:10px;padding:9px 12px;border-left:3px solid transparent;
 transition:.13s;color:inherit}
.pick:hover{background:var(--surface2);text-decoration:none}
.pick.on{background:var(--brandsoft);border-left-color:var(--brand)}
.pick .n{font-size:13px;font-weight:600;line-height:1.3}
.pick .e{font-size:11.5px;color:var(--muted);line-height:1.3}
.mailrow{border-bottom:1px solid var(--line2);padding:13px 15px;transition:.13s}
.mailrow:last-child{border-bottom:0}
.mailrow:hover{background:var(--surface2)}
.mtop{display:flex;align-items:center;gap:11px;flex-wrap:wrap}
.mtop .sj{font-size:14px;font-weight:650}
.macts{display:flex;gap:7px;margin-top:9px;flex-wrap:wrap}
.unread{width:7px;height:7px;border-radius:50%;background:var(--brand);flex:none}
.rhero{text-align:center;padding:34px 26px 30px;border-radius:16px;color:#fff;
 background:linear-gradient(135deg,#dc2626,#b91c1c);box-shadow:0 8px 28px rgba(220,38,38,.3)}
.rhero.good{background:linear-gradient(135deg,#059669,#047857);box-shadow:0 8px 28px rgba(5,150,105,.28)}
.rhero .ico{font-size:44px;line-height:1;margin-bottom:12px}
.rhero h2{font-size:23px;margin-bottom:8px}
.rhero p{margin:0;opacity:.92;font-size:14.5px;max-width:56ch;margin-inline:auto}
.flag{background:var(--surface);border:1px solid var(--line);border-radius:var(--r);padding:15px 17px;box-shadow:var(--sh)}
.flag .fh{font-size:12.5px;font-weight:700;color:var(--bad);display:flex;align-items:center;gap:8px;margin-bottom:6px}
.flag p{margin:0;font-size:13.5px;color:var(--ink2);line-height:1.6}
.q{border:1px solid var(--line);border-radius:var(--r);padding:17px 18px;background:var(--surface);
 box-shadow:var(--sh);margin-bottom:13px}
.q .qh{display:flex;gap:11px;margin-bottom:12px}
.q .qn{width:25px;height:25px;border-radius:8px;background:var(--brandsoft);color:var(--brand);
 display:grid;place-items:center;font-size:12px;font-weight:800;flex:none}
.q .qt{font-size:14.5px;font-weight:640;line-height:1.45}
.opts{display:flex;flex-direction:column;gap:8px}
.opt{display:flex;align-items:center;gap:10px;padding:9px 13px;border:1px solid var(--line);
 border-radius:9px;cursor:pointer;transition:.13s;font-size:13.5px;background:var(--surface2)}
.opt:hover{border-color:var(--brand2);background:var(--brandsoft)}
.opt input{width:auto;margin:0;accent-color:var(--brand)}
.scorebig{font-size:52px;font-weight:750;letter-spacing:-.04em;line-height:1;
 background:linear-gradient(135deg,#4f46e5,#059669);-webkit-background-clip:text;
 -webkit-text-fill-color:transparent;background-clip:text}

/* ---------------- printable report ---------------- */
.report{background:#fff;color:#111;max-width:900px;margin:0 auto;padding:42px 46px;
 border:1px solid var(--line);box-shadow:var(--sh)}
.report h1{font-size:23px;margin-bottom:4px}
.report h2{font-size:16px;margin:26px 0 8px;padding-bottom:5px;border-bottom:1px solid #ddd}
.report h3{font-size:13.5px;margin:16px 0 6px}
.report p,.report li{font-size:12.5px;line-height:1.65}
.report table{font-size:11.5px}
.report th{font-size:9.5px;padding:0 6px 6px}
.report td{padding:6px;border-bottom:1px solid #eee}
.report .meta{font-size:11.5px;color:#555}
.report .kpis{display:grid;grid-template-columns:repeat(4,1fr);gap:10px;margin:16px 0}
.report .kpi{border:1px solid #e3e3e3;box-shadow:none;padding:10px 12px}
.report .kpi .k-val{font-size:20px}
.report .kpi .k-lbl{font-size:9px}
.report .note{background:#f6f6f6;border-color:#e3e3e3;color:#333}
@media print{
 .sb,.topbar,.simbar,.no-print{display:none!important}
 .shell{display:block}
 .wrap{max-width:none;padding:0}
 .report{border:0;box-shadow:none;padding:0;max-width:none}
 body{background:#fff}
 @page{size:A4;margin:18mm 16mm}
 a{color:#000;text-decoration:none}
 .report tr,.report .card{break-inside:avoid}
}
"""

DEPT_COLOR = {"IT": "#6366f1", "HR": "#ec4899", "Finance": "#f59e0b",
              "Sales": "#10b981", "Operations": "#0ea5e9", "Legal": "#8b5cf6",
              "General": "#64748b"}

STATUS_CHIP = {
    "Draft": "mute", "Scheduled": "info", "Active": "ok",
    "Paused": "warn", "Completed": "brand", "Archived": "mute",
}
OUTCOME_CHIP = {
    "submitted": ("bad", "❌", "Submitted"),
    "clicked": ("warn", "⚠", "Clicked"),
    "reported": ("ok", "✅", "Reported"),
    "opened": ("info", "👁", "Opened"),
    "sent": ("mute", "•", "No response"),
}
RISK_COLOR = {"Low": "#059669", "Moderate": "#d97706", "High": "#ea580c", "Critical": "#dc2626"}


def esc(value) -> str:
    return html.escape("" if value is None else str(value), quote=True)


def avatar(name: str, dept: str, big: bool = False) -> str:
    initials = "".join(part[0] for part in (name or "?").split()[:2]).upper()
    color = DEPT_COLOR.get(dept, DEPT_COLOR["General"])
    return f'<div class="av{" lg" if big else ""}" style="background:{color}">{esc(initials)}</div>'


def chip(text: str, cls: str = "mute", dot: bool = False) -> str:
    d = "<span class=dot></span>" if dot else ""
    return f'<span class="chip {cls}">{d}{esc(text)}</span>'


def status_chip(status: str) -> str:
    return chip(status, STATUS_CHIP.get(status, "mute"), dot=True)


def risk_badge(band: str) -> str:
    return f'<span class="badge-risk {esc(band)}">{esc(band)}</span>'


def kpi(label: str, value, sub: str, icon: str, color: str, soft: str) -> str:
    return (f'<div class=kpi style="--k:{color};--ksoft:{soft}">'
            f'<div class=k-ico>{icon}</div><div class=k-lbl>{esc(label)}</div>'
            f'<div class=k-val>{value}</div><div class=k-sub>{esc(sub)}</div></div>')


def funnel(stats: dict, steps=None) -> str:
    steps = steps or [("Sent", "sent", "#4f46e5"), ("Opened", "opened", "#2563eb"),
                      ("Clicked", "clicked", "#f59e0b"), ("Submitted", "submitted", "#dc2626")]
    mx = max(1, stats.get("sent", 0))
    rows = "".join(
        f'<div class=fn-row><span class=fn-lbl>{label}</span>'
        f'<div class=fn-track><div class=fn-fill style="width:{100 * stats.get(key, 0) / mx:.1f}%;background:{color}"></div></div>'
        f'<span class=fn-val>{stats.get(key, 0)} <em>/{stats.get("sent", 0)}</em></span></div>'
        for label, key, color in steps)
    return f'<div class=funnel>{rows}</div>'


def donut(segments, center_top: str, center_sub: str) -> str:
    total = sum(v for _, v, _ in segments) or 1
    r, circ = 54, 2 * 3.14159265 * 54
    offset, parts = 0.0, []
    for _, value, color in segments:
        if value <= 0:
            continue
        dash = value / total * circ
        parts.append(f'<circle cx="70" cy="70" r="{r}" fill="none" stroke="{color}" stroke-width="19"'
                     f' stroke-dasharray="{dash:.2f} {circ - dash:.2f}" stroke-dashoffset="{-offset:.2f}"'
                     f' stroke-linecap="butt" transform="rotate(-90 70 70)"/>')
        offset += dash
    svg = (f'<svg viewBox="0 0 140 140" class="donut">'
           f'<circle cx="70" cy="70" r="{r}" fill="none" stroke="#eef1f7" stroke-width="19"/>'
           + "".join(parts) +
           f'<text x="70" y="68" text-anchor="middle" class="donut-c">{esc(center_top)}</text>'
           f'<text x="70" y="82" text-anchor="middle" class="donut-s">{esc(center_sub)}</text></svg>')
    legend = "".join(
        f'<div class=lg><span class=sw style="background:{color}"></span>{esc(label)}<b>{value}</b></div>'
        for label, value, color in segments)
    return f'<div class=donutwrap>{svg}<div class=legend>{legend}</div></div>'


def department_bars(rows, metric: str = "submit_rate") -> str:
    out = ""
    for row in rows:
        pct_value = row.get(metric, 0)
        color = DEPT_COLOR.get(row["department"], DEPT_COLOR["General"])
        out += (f'<div class=dp><span class=dp-n>{esc(row["department"])}</span>'
                f'<span class=dp-v>{row["submitted"]}/{row["sent"]} phished &nbsp;·&nbsp; <b>{pct_value}%</b></span>'
                f'<div class=dp-track><div class=dp-fill style="width:{min(100, pct_value)}%;background:{color}"></div></div></div>')
    return f'<div class=dept>{out}</div>' if out else '<div class=empty>No data yet.</div>'


def risk_bar(score: float, band: str) -> str:
    color = RISK_COLOR.get(band, "#64748b")
    return (f'<div class=riskbar><div class=t><div class=f style="width:{min(100, score)}%;background:{color}"></div></div>'
            f'<b style="font-size:12px;color:{color}">{score:.0f}</b></div>')


def sparkline(values, color: str = "#4f46e5", height: int = 56, width: int = 320) -> str:
    values = [float(v) for v in values] or [0]
    lo, hi = min(values), max(values)
    span = (hi - lo) or 1
    pad = 6
    pts = []
    for i, value in enumerate(values):
        x = pad + i * (width - 2 * pad) / max(1, len(values) - 1)
        y = height - pad - (value - lo) / span * (height - 2 * pad)
        pts.append(f"{x:.1f},{y:.1f}")
    area = f"{pad},{height - pad} " + " ".join(pts) + f" {width - pad},{height - pad}"
    return (f'<svg class=spark viewBox="0 0 {width} {height}" preserveAspectRatio="none">'
            f'<polygon points="{area}" fill="{color}" opacity=".08"/>'
            f'<polyline points="{" ".join(pts)}" fill="none" stroke="{color}" stroke-width="2" '
            f'stroke-linejoin="round" stroke-linecap="round"/></svg>')


def empty_state(icon: str, title: str, body: str, action: str = "") -> str:
    return (f'<div class=empty><div class=ic>{icon}</div><b>{esc(title)}</b>'
            f'<div>{body}</div>{action}</div>')


def nav_admin(active: str, admin: dict, pending: int = 0) -> str:
    groups = [
        ("Workspace", [
            ("/", "Dashboard", "◫"),
            ("/campaigns", "Campaigns", "◈"),
            ("/templates", "Lures", "✉"),
            ("/people", "People", "☺"),
        ]),
        ("Insight", [
            ("/analytics", "Analytics", "◔"),
            ("/training", "Training", "◉"),
            ("/report", "Report", "▤"),
        ]),
        ("System", [
            ("/audit", "Audit log", "≡"),
            ("/settings", "Settings", "⚙"),
        ]),
    ]
    out = []
    for label, items in groups:
        out.append(f'<div class=grp>{label}</div>')
        for href, text, icon in items:
            on = " on" if active == href else ""
            badge = ""
            if href == "/campaigns" and pending:
                badge = f'<span class="chip warn" style="margin-left:auto">{pending}</span>'
            out.append(f'<a class="item{on}" href="{href}"><span class=ic>{icon}</span>{text}{badge}</a>')
    initials = "".join(p[0] for p in (admin.get("display_name") or admin["username"]).split()[:2]).upper()
    return f"""<aside class=sb>
 <a class=brand href="/"><span class=logo>🎣</span>PhishStudy</a>
 {''.join(out)}
 <div class=whoami><div class=av style="background:#4338ca">{esc(initials)}</div>
  <div><div class=nm>{esc(admin.get('display_name') or admin['username'])}</div>
  <div class=rl>Administrator</div></div>
  <form method=post action="/logout" style="margin-left:auto">{'<input type=hidden name=csrf value="' + esc(admin['csrf']) + '">' if admin.get('csrf') else ''}
   <button class=btn type=submit title="Sign out" style="color:#9fb0c9;padding:4px 6px">⏻</button></form>
 </div></aside>"""


def page_admin(title: str, body: str, active: str, admin: dict, *, crumb: str = "",
               actions: str = "", pending: int = 0, maxw: str = "", flash: str = "",
               flash_kind: str = "ok") -> str:
    banner = f'<div class="note {flash_kind}" style="margin-bottom:16px">{esc(flash)}</div>' if flash else ""
    return f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{esc(title)} · PhishStudy</title><style>{CSS}</style></head><body>
<div class=simbar>🔒 SIMULATION FOR EDUCATION ONLY <span>— no real email is sent; every employee, mail and credential in this system is fictional</span></div>
<div class=shell>{nav_admin(active, admin, pending)}
 <main class=main>
  <div class=topbar><div class=crumb><a href="/">PhishStudy</a> › <b>{esc(crumb or title)}</b></div>
   <div class=topact>{actions}</div></div>
  <div class="wrap {maxw}">{banner}{body}
   <div class=foot><span>Phishing Susceptibility Study · BE Honours Major Project · Department of Information Technology</span>
   <span>Simulation only — no real credentials are ever stored</span></div>
  </div>
 </main>
</div></body></html>"""


def page_public(title: str, body: str, *, wide: bool = False) -> str:
    return f"""<!doctype html><html lang=en><head><meta charset=utf-8>
<meta name=viewport content="width=device-width,initial-scale=1">
<title>{esc(title)} · PhishStudy</title><style>{CSS}</style></head><body class=participant>
<div class=simbar>🔒 SIMULATION FOR EDUCATION ONLY <span>— this is a fictional message used in a phishing-awareness exercise</span></div>
<div class=wrap style="max-width:{'1000' if wide else '860'}px;padding-top:26px">{body}</div>
</body></html>"""
