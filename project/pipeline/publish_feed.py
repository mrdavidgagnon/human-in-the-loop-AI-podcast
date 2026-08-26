from pathlib import Path
from datetime import datetime, timezone
from xml.sax.saxutils import escape
import shutil, subprocess, re, sys

ROOT=Path(__file__).resolve().parent.parent
SITE=ROOT/'feed-site'
BASE_URL='https://mrdavidgagnon.github.io/human-in-the-loop-AI-podcast'
EP=[
('002','Can We See Learning in the Game?','can-we-see-learning-in-the-game.mp3','A playful, dramatized interview with fictional research correspondent Dr. Rowan Field about game learning analytics, standards, traces, inference, knowledge models, prevalence, and the limits of dashboards.','episode-002-can-we-see-learning-in-the-game','episode-002'),
('003','When a Game Needs a Teacher','when-a-game-needs-a-teacher.mp3','A playful, dramatized interview with fictional research correspondent Dr. Rowan Field about scaffolding, GenAI support, collaborative inquiry, debriefing, feedback, cognitive load, and formative assessment in game-based learning.','episode-003-when-a-game-needs-a-teacher','episode-003'),
('004','The Feeling Learner and the Evidence Trail','the-feeling-learner-and-the-evidence-trail.mp3','A playful, dramatized interview with fictional research correspondent Dr. Rowan Field about emotion, affective design, serious games, narrative, transfer, and making evidence trails visible.','episode-004-the-feeling-learner-and-the-evidence-trail','episode-004'),
('005','What Can a Hundred Games Teach a Teacher?','what-can-a-hundred-games-teach-a-teacher.mp3','A playful, dramatized single-source interview with fictional research correspondent Dr. Rowan Field about Karen Schrier’s edited collection of classroom game examples and the limits of design guidance.','episode-005-what-can-a-hundred-games-teach-a-teacher','episode-005'),
('006','Can Play Become Evidence?','can-play-become-evidence.mp3','A playful, dramatized single-source interview with fictional research correspondent Dr. Rowan Field about Playful Testing, formative assessment games, and the limits of inferring learning from play.','episode-006-can-play-become-evidence','episode-006')]

def duration(path):
    sys.path.insert(0,'/data/.openclaw/tools/two-voice-tts')
    import imageio_ffmpeg
    x=subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-i',str(path)],capture_output=True,text=True).stderr
    m=re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)',x)
    sec=int(m.group(1))*3600+int(m.group(2))*60+round(float(m.group(3))) if m else 0
    return f'{sec//3600:02d}:{(sec%3600)//60:02d}:{sec%60:02d}'

def notes_html(num):
    t=(ROOT/'episodes'/num/'episode-notes.md').read_text()
    # Keep feed notes concise while preserving the direct notes link, disclosures,
    # and a complete source list in the RSS extended content.
    links=[]
    for line in t.splitlines():
        if re.match(r'^\d+\.\s+', line):
            links.append(re.sub(r'^\d+\.\s+', '', line))
    return '<p>This is a synthetic/dramatized interview with fictional research correspondent Dr. Rowan Field. Rowan is a fictional composite; no cited author was interviewed or is speaking through Rowan. Dialogue paraphrases and synthesizes the research, preserves evidence limits, and contains no fabricated author quotations.</p><p>This is an AI-generated summary that may contain errors and is not a substitute for reading the cited sources.</p><p><a href="episode-'+num+'-notes.md">Full source notes, evidence limitations, and direct Zotero links</a></p><ol>'+''.join('<li>'+escape(x)+'</li>' for x in links)+'</ol>'

def main():
    for num,title,fn,desc,guid,base in EP:
        src=ROOT/'episodes'/num/fn; dst=SITE/(base+'.mp3'); shutil.copy2(src,dst); shutil.copy2(ROOT/'episodes'/num/'episode-notes.md',SITE/(base+'-notes.md'))
    items=[]
    # Preserve the existing pilot entry verbatim enough for stable GUID and links.
    items.append(f'''      <item><title>When AI Joins Educational Inquiry, What Should Remain Human?</title><description>A playful, dramatized interview with a fictional research correspondent synthesizing five studies about AI-assisted qualitative analysis, educational ethics, and teacher-facing learning analytics. This is not an actual interview with any author.</description><content:encoded><![CDATA[<p>A playful, dramatized interview with fictional research correspondent Dr. Rowan Field. Rowan is a fictional composite; no cited author was interviewed or is speaking through Rowan. The dialogue paraphrases the research and is an AI-generated summary that may contain errors; it is not an actual author interview or a substitute for reading the sources.</p><p><a href="episode-001-notes.md">Existing episode source notes</a></p>]]></content:encoded><guid isPermaLink="false">human-in-the-loop-episode-001-ai-educational-inquiry</guid><pubDate>Wed, 26 Aug 2026 03:02:00 +0000</pubDate><enclosure url="{BASE_URL}/human-in-the-loop-interview.mp3" length="4278956" type="audio/mpeg"/><itunes:duration>04:27</itunes:duration><itunes:episode>1</itunes:episode><itunes:episodeType>full</itunes:episodeType><itunes:explicit>false</itunes:explicit><itunes:image href="{BASE_URL}/cover.png"/></item>''')
    now='Wed, 26 Aug 2026 03:45:00 +0000'
    for num,title,fn,desc,guid,base in EP:
        p=SITE/(base+'.mp3'); items.append(f'''      <item><title>{escape(title)}</title><description>{escape(desc)}</description><content:encoded><![CDATA[{notes_html(num)}]]></content:encoded><guid isPermaLink="false">human-in-the-loop-{guid}</guid><pubDate>{now}</pubDate><enclosure url="{BASE_URL}/{base}.mp3" length="{p.stat().st_size}" type="audio/mpeg"/><itunes:duration>{duration(p)}</itunes:duration><itunes:episode>{int(num)}</itunes:episode><itunes:episodeType>full</itunes:episodeType><itunes:explicit>false</itunes:explicit><itunes:image href="{BASE_URL}/cover.png"/></item>''')
    xml=f'''<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd" xmlns:content="http://purl.org/rss/1.0/modules/content/"><channel><title>Human in the Loop</title><link>{BASE_URL}/</link><description>Playful, dramatized interviews synthesizing research about learning, technology, and human judgment. Private unlisted review feed.</description><language>en-us</language><copyright>© 2026 Field Day Lab, UW–Madison</copyright><itunes:author>Field Day Lab, UW–Madison</itunes:author><itunes:explicit>false</itunes:explicit><itunes:type>episodic</itunes:type><itunes:category text="Education"/><itunes:image href="{BASE_URL}/cover.png"/><image><url>{BASE_URL}/cover.png</url><title>Human in the Loop</title><link>{BASE_URL}/</link></image>\n'''+ '\n'.join(items)+'\n</channel></rss>\n'
    (SITE/'feed.xml').write_text(xml)
    (SITE/'index.html').write_text('''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="robots" content="noindex,nofollow"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Human in the Loop</title></head><body><h1>Human in the Loop</h1><p>Private, unlisted research-review podcast feed.</p><p><a href="feed.xml">RSS feed</a> · <a href="needs-full-text.html">Full-text queue</a></p><h2>Episodes</h2><ul><li><a href="human-in-the-loop-interview.mp3">Episode 001 — When AI Joins Educational Inquiry, What Should Remain Human?</a></li><li><a href="episode-002-can-we-see-learning-in-the-game.mp3">Episode 002 — Can We See Learning in the Game?</a> · <a href="episode-002-notes.md">notes</a></li><li><a href="episode-003-when-a-game-needs-a-teacher.mp3">Episode 003 — When a Game Needs a Teacher</a> · <a href="episode-003-notes.md">notes</a></li><li><a href="episode-004-the-feeling-learner-and-the-evidence-trail.mp3">Episode 004 — The Feeling Learner and the Evidence Trail</a> · <a href="episode-004-notes.md">notes</a></li><li><a href="episode-005-what-can-a-hundred-games-teach-a-teacher.mp3">Episode 005 — What Can a Hundred Games Teach a Teacher?</a> · <a href="episode-005-notes.md">notes</a></li><li><a href="episode-006-can-play-become-evidence.mp3">Episode 006 — Can Play Become Evidence?</a> · <a href="episode-006-notes.md">notes</a></li></ul></body></html>''')
    print('published local feed',len(items),'items')
if __name__=='__main__': main()
