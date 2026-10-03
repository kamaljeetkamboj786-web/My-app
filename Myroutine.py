import streamlit as st
from datetime import date, timedelta
import json
from pathlib import Path
import calendar

st.set_page_config(page_title="GlowUp Daily ✨", page_icon="✨", layout="wide")

DATA = Path("glowup_data.json")

ROUTINE = [
    ("🌅","Wake up + freshen up","07:00","Lifestyle"),
    ("💧","2 glasses of water","07:15","Hydration"),
    ("🍳","Breakfast + protein","08:00","Diet"),
    ("🧴","Morning skincare + sunscreen","09:00","Skincare"),
    ("💧","Water break","10:30","Hydration"),
    ("🍌","Healthy snack","11:30","Diet"),
    ("🍛","Lunch + protein","13:30","Diet"),
    ("💧","Water break","15:30","Hydration"),
    ("🏋️","Workout","17:00","Fitness"),
    ("🥛","Evening snack / shake","18:00","Diet"),
    ("🧴","Night skincare","21:00","Skincare"),
    ("📵","Wind down / no-phone","22:00","Lifestyle"),
    ("😴","Sleep","22:30","Lifestyle"),
]

BADGES = [
    (1,"🌱","First Step","Complete your first day"),
    (3,"💗","3-Day Glow","Keep a 3-day streak"),
    (7,"🔥","Week Warrior","Keep a 7-day streak"),
    (14,"✨","Glow Getter","Keep a 14-day streak"),
    (21,"👑","Consistency Queen","Keep a 21-day streak"),
    (30,"🏆","30-Day Glow","Complete the 30-day challenge"),
]

def load():
    if DATA.exists():
        try: return json.loads(DATA.read_text())
        except: pass
    return {"days":{}, "weights":[], "goal":45, "challenge_start":str(date.today())}

def save(d): DATA.write_text(json.dumps(d,indent=2))

data=load()
data.setdefault("days",{})
data.setdefault("weights",[])
data.setdefault("goal",45)
data.setdefault("challenge_start",str(date.today()))

def completion(day):
    states=data["days"].get(str(day),{})
    done=sum(bool(states.get(n,False)) for _,n,_,_ in ROUTINE)
    return done, len(ROUTINE)

def qualifies(day):
    done,total=completion(day)
    return done >= total/2

def current_streak():
    s=0; d=date.today()
    while qualifies(d):
        s+=1; d-=timedelta(days=1)
    return s

def longest_streak():
    dates=sorted({date.fromisoformat(k) for k in data["days"] if qualifies(date.fromisoformat(k))})
    best=cur=0; prev=None
    for d in dates:
        if prev and d==prev+timedelta(days=1): cur+=1
        else: cur=1
        best=max(best,cur); prev=d
    return best

def level(streak):
    if streak>=30:return 6,"Glow Legend","🏆"
    if streak>=21:return 5,"Consistency Queen","👑"
    if streak>=14:return 4,"Glow Getter","✨"
    if streak>=7:return 3,"Week Warrior","🔥"
    if streak>=3:return 2,"Glow Starter","💗"
    return 1,"Fresh Start","🌱"

def badge_unlocked(days):
    return [b for b in BADGES if days>=b[0]]

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;500;600;700&display=swap');
html,body,[class*="css"]{font-family:Poppins,sans-serif}
.stApp{background:linear-gradient(135deg,#fff3fa,#f7f0ff 50%,#eef7ff)}
.block-container{max-width:1180px;padding-top:1rem}
.hero{padding:28px;border-radius:30px;background:linear-gradient(135deg,#ff70b7,#9867ff);
color:white;box-shadow:0 14px 35px #8b5cf633;margin-bottom:18px}
.hero h1{margin:0;font-size:2.25rem}.hero p{margin:6px 0 0}
.card{background:#ffffffd9;border-radius:22px;padding:18px;box-shadow:0 8px 25px #8b5cf615;border:1px solid #fff;margin-bottom:14px}
.stat{text-align:center;background:white;border-radius:20px;padding:15px;box-shadow:0 6px 20px #8b5cf615}
.num{font-size:1.8rem;font-weight:700;color:#8b5cf6}.small{color:#777;font-size:.82rem}
.badge{background:white;border-radius:20px;padding:15px;text-align:center;box-shadow:0 7px 20px #8b5cf615;height:145px}
.badge.lock{opacity:.38;filter:grayscale(1)}
.badge-icon{font-size:2rem}.badge-title{font-weight:700;color:#7c4dce}
.calendar-day{padding:9px;border-radius:14px;text-align:center;background:white;margin:3px}
.done{background:#eadcff}.today{border:2px solid #a66cff}
.stButton>button{border-radius:14px;font-weight:600}
</style>
""",unsafe_allow_html=True)

st.sidebar.title("✨ GlowUp Daily")
page=st.sidebar.radio("Menu",["🏠 Today","📅 Calendar","🔥 30-Day Challenge","🏅 Badges & Levels","📈 Progress"])

today=date.today()
done,total=completion(today)
pct=int(done/total*100)
st.markdown(f'<div class="hero"><h1>✨ GlowUp Daily</h1><p>{today.strftime("%A, %d %B %Y")} • Your glow-up is built one habit at a time 💗</p></div>',unsafe_allow_html=True)

if page=="🏠 Today":
    c=st.columns(4)
    stats=[("Today",f"{pct}%"),("Tasks",f"{done}/{total}"),("🔥 Streak",f"{current_streak()} days"),("🏆 Level",str(level(current_streak())[0]))]
    for col,(a,b) in zip(c,stats):
        col.markdown(f'<div class="stat"><div class="small">{a}</div><div class="num">{b}</div></div>',unsafe_allow_html=True)
    st.write("")
    st.progress(pct/100)
    st.subheader("🕐 Your Daily Schedule")

    for idx,(icon,name,tm,cat) in enumerate(ROUTINE):
        checked=data["days"].get(str(today),{}).get(name,False)
        # Unique key prevents StreamlitDuplicateElementKey errors.
        widget_key=f"routine_{today}_{idx}_{name.replace(' ','_')}"
        new=st.checkbox(
            f"{icon} **{tm} — {name}**  ·  {cat}",
            value=checked,
            key=widget_key
        )
        if new!=checked:
            data["days"].setdefault(str(today),{})[name]=new
            save(data); st.rerun()

    st.info("🔥 A day counts toward your streak when you complete at least half of your routine.")

elif page=="📅 Calendar":
    st.subheader("📅 Beautiful Routine Calendar")
    year=st.number_input("Year",2024,2100,today.year)
    month=st.selectbox("Month",range(1,13),index=today.month-1,format_func=lambda x:calendar.month_name[x])
    weeks=calendar.monthcalendar(year,month)
    heads=["Mon","Tue","Wed","Thu","Fri","Sat","Sun"]
    cols=st.columns(7)
    for col,h in zip(cols,heads): col.markdown(f"**{h}**")
    for week in weeks:
        cols=st.columns(7)
        for i,daynum in enumerate(week):
            if daynum==0: continue
            d=date(year,month,daynum); n,_=completion(d)
            p=int(n/total*100)
            emoji="🔥" if p>=50 else ("🌱" if p>0 else "○")
            cls="today" if d==today else ""
            cols[i].markdown(f'<div class="calendar-day {cls}"><b>{daynum}</b><br>{emoji}<br><span class="small">{p}%</span></div>',unsafe_allow_html=True)
    st.caption("🔥 = streak day • 🌱 = started • ○ = no completed routine")

elif page=="🔥 30-Day Challenge":
    st.subheader("🔥 30-Day Glow Challenge")
    start=date.fromisoformat(data["challenge_start"])
    day_index=(today-start).days+1
    if day_index<1: day_index=1
    if day_index>30: day_index=30
    challenge_done=sum(1 for i in range(30) if qualifies(start+timedelta(days=i)))
    st.markdown(f'<div class="card"><h2>Day {day_index}/30</h2><p>Challenge progress: <b>{challenge_done}/30 days</b></p></div>',unsafe_allow_html=True)
    st.progress(challenge_done/30)
    cols=st.columns(10)
    for i in range(30):
        d=start+timedelta(days=i)
        ok=qualifies(d)
        cols[i%10].markdown(f'<div class="calendar-day {"done" if ok else ""}"><b>{i+1}</b><br>{"🔥" if ok else "○"}</div>',unsafe_allow_html=True)
    if st.button("🔄 Start a new 30-day challenge"):
        data["challenge_start"]=str(today); save(data); st.rerun()

elif page=="🏅 Badges & Levels":
    s=current_streak(); lv,name,icon=level(s)
    st.markdown(f'<div class="hero"><h1>{icon} Level {lv} — {name}</h1><p>Current streak: {s} days • Longest streak: {longest_streak()} days</p></div>',unsafe_allow_html=True)
    st.subheader("🏅 Badges")
    cols=st.columns(3)
    unlocked={b[0] for b in badge_unlocked(s)}
    for i,(days,bicon,title,desc) in enumerate(BADGES):
        lock="" if days in unlocked else "lock"
        status="Unlocked 🎉" if days in unlocked else f"Reach {days} days"
        cols[i%3].markdown(f'<div class="badge {lock}"><div class="badge-icon">{bicon}</div><div class="badge-title">{title}</div><div class="small">{desc}</div><div class="small">{status}</div></div>',unsafe_allow_html=True)
        cols[i%3].write("")

elif page=="📈 Progress":
    st.subheader("📈 Your Progress")
    c1,c2=st.columns(2)
    with c1:
        current=st.number_input("Current weight (kg)",20.0,150.0,float(data["weights"][-1]["weight"]) if data["weights"] else 37.0,0.1)
        if st.button("Save weight"):
            data["weights"].append({"date":str(today),"weight":current}); save(data); st.success("Saved 💗")
    with c2:
        goal=st.number_input("Goal weight (kg)",20.0,150.0,float(data["goal"]),0.5)
        if goal!=data["goal"]: data["goal"]=goal; save(data)
    if data["weights"]:
        st.line_chart({"Weight (kg)":{x["date"]:x["weight"] for x in data["weights"]}})
    else: st.info("Add your weight to start your chart.")
    st.markdown(f'<div class="card"><h3>🔥 Streak stats</h3>Current: {current_streak()} days<br>Longest: {longest_streak()} days<br>30-day challenge: {sum(1 for i in range(30) if qualifies(date.fromisoformat(data["challenge_start"])+timedelta(days=i)))}/30 days</div>',unsafe_allow_html=True)

st.caption("✨ GlowUp Daily • Consistency over perfection 💗")
