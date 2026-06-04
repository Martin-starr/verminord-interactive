/**
 * Google Apps Script — alternativ til GitHub Action.
 *
 * OPPSETT:
 * 1. Åpne arket i Google Sheets → Utvidelser → Apps Script
 * 2. Lim inn denne fila
 * 3. Sett GITHUB_TOKEN og REPO i Script Properties (Prosjektinnstillinger → Skriptegenskaper)
 * 4. Legg til tidsutløser: syncToGitHub(), daglig kl 06:00
 *
 * Script Properties:
 *   GITHUB_TOKEN  — Personal access token med repo-tilgang
 *   REPO          — f.eks. "martin-starr/verminord-interactive"
 *   BRANCH        — f.eks. "master" (standard)
 */

// ── Config ──────────────────────────────────────────────────────────────────

var PRODUCTION_TAB = "Worm Production";
var PRECOMPOST_TAB = "Pre-Compost";

var COL = { DATE:0, BIN:1, FEED:2, ADDED:3, MOISTURE:4, TEMP:5, PH:6, COMMENT:7, SOURCE:8 };

var RANGES = [
  {key:"7D",label:"7 DGR",n:7},{key:"21D",label:"21 DGR",n:21},
  {key:"3M",label:"3 MND",n:90},{key:"6M",label:"6 MND",n:180},
  {key:"YTD",label:"I ÅR",n:-1},{key:"ALL",label:"ALT",n:-2}
];

var SYSTEMS = [
  {id:"cft1",name:"CFT1",group:"prod",targets:{temp:[15,25],fukt:[60,80],ph:[6.0,8.0]}},
  {id:"cft2",name:"CFT2",group:"prod",targets:{temp:[15,25],fukt:[60,80],ph:[6.0,8.0]}},
  {id:"cft3",name:"CFT3",group:"prod",targets:{temp:[15,25],fukt:[60,80],ph:[6.0,8.0]}},
  {id:"wedge1",name:"Wedge 1",group:"prod",targets:{temp:[15,25],fukt:[60,80],ph:[6.0,8.0]}},
  {id:"wedge2",name:"Wedge 2",group:"prod",targets:{temp:[15,25],fukt:[60,80],ph:[6.0,8.0]}},
  {id:"breeder",name:"Breeder",group:"prod",targets:{temp:[15,25],fukt:[60,80],ph:[6.0,8.0]}},
  {id:"forkompost1",name:"Forkompost 1",group:"precompost",targets:{temp:[55,80],fukt:[50,70],ph:[6.0,8.5]},threshold:55,required:5},
  {id:"forkompost2",name:"Forkompost 2",group:"precompost",targets:{temp:[55,80],fukt:[50,70],ph:[6.0,8.5]},threshold:55,required:5}
];

// Epoch map: {start, end (null=ongoing), tab, bin} → system
var EPOCH_MAP = [
  {start:"2025-07-01",end:"2025-10-31",tab:"production",bin:1,system:"wedge1"},
  {start:"2025-07-01",end:"2025-10-31",tab:"production",bin:2,system:"wedge2"},
  {start:"2025-11-01",end:"2026-01-31",tab:"production",bin:1,system:"cft1"},
  {start:"2025-11-01",end:"2026-01-31",tab:"production",bin:2,system:"cft2"},
  {start:"2025-11-01",end:"2026-01-31",tab:"production",bin:3,system:"cft3"},
  {start:"2025-11-01",end:"2026-01-31",tab:"production",bin:4,system:"wedge1"},
  {start:"2026-02-01",end:null,tab:"production",bin:1,system:"cft1"},
  {start:"2026-02-01",end:null,tab:"production",bin:2,system:"cft2"},
  {start:"2026-02-01",end:null,tab:"production",bin:3,system:"cft3"},
  {start:"2026-02-01",end:null,tab:"production",bin:4,system:"wedge1"},
  {start:"2026-02-01",end:null,tab:"production",bin:5,system:"wedge2"},
  {start:"2026-02-01",end:null,tab:"production",bin:6,system:"breeder"},
  {start:"2025-07-01",end:null,tab:"precompost",bin:1,system:"forkompost1"},
  {start:"2025-07-01",end:null,tab:"precompost",bin:2,system:"forkompost2"}
];

// ── Entry point ─────────────────────────────────────────────────────────────

function syncToGitHub() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var today = new Date();

  var prodRows = readTab_(ss, PRODUCTION_TAB);
  var preRows  = readTab_(ss, PRECOMPOST_TAB);

  var prodRecs = parseRows_(prodRows);
  var preRecs  = parseRows_(preRows);

  var data = buildDataJson_(prodRecs, preRecs, today);
  var json = JSON.stringify(data, null, 2);

  pushToGitHub_(json);
  Logger.log("Synkronisert data.json — %s systemer, %s avvik", data.SYSTEMS.length, data.KPIS.avvik);
}

// ── Sheet reading ───────────────────────────────────────────────────────────

function readTab_(ss, tabName) {
  var sheet = ss.getSheetByName(tabName);
  if (!sheet) { Logger.log("Finner ikke tab: " + tabName); return []; }
  return sheet.getDataRange().getValues();
}

function parseRows_(rows) {
  var records = [];
  for (var i = 0; i < rows.length; i++) {
    var row = rows[i];
    var d = parseDate_(row[COL.DATE]);
    if (!d) continue;
    var bin = parseInt(row[COL.BIN], 10);
    if (isNaN(bin)) continue;

    records.push({
      date: d,
      bin: bin,
      temp: parseNum_(row[COL.TEMP]),
      moisture: parseNum_(row[COL.MOISTURE]),
      ph: parseNum_(row[COL.PH]),
      comment: String(row[COL.COMMENT] || "")
    });
  }
  return records;
}

function parseDate_(v) {
  if (v instanceof Date && !isNaN(v)) return v;
  var s = String(v).trim();
  var m = s.match(/^(\d{1,2})\/(\d{1,2})\/(\d{4})$/);
  if (m) return new Date(+m[3], +m[2]-1, +m[1]);
  var d = new Date(s);
  return isNaN(d) ? null : d;
}

function parseNum_(v) {
  if (typeof v === "number") return v;
  var n = parseFloat(String(v).replace(",", "."));
  return isNaN(n) ? null : n;
}

// ── Epoch → System ──────────────────────────────────────────────────────────

function resolveSystem_(d, bin, tabKey) {
  for (var i = 0; i < EPOCH_MAP.length; i++) {
    var ep = EPOCH_MAP[i];
    if (ep.tab !== tabKey || ep.bin !== bin) continue;
    var start = new Date(ep.start);
    var end = ep.end ? new Date(ep.end) : new Date(2099, 11, 31);
    if (d >= start && d <= end) return ep.system;
  }
  return null;
}

// ── Build data.json ─────────────────────────────────────────────────────────

function buildDataJson_(prodRecs, preRecs, today) {
  var bySystem = {};
  SYSTEMS.forEach(function(s){ bySystem[s.id] = []; });

  prodRecs.forEach(function(r){
    var sid = resolveSystem_(r.date, r.bin, "production");
    if (sid && bySystem[sid]) bySystem[sid].push(r);
  });
  preRecs.forEach(function(r){
    var sid = resolveSystem_(r.date, r.bin, "precompost");
    if (sid && bySystem[sid]) bySystem[sid].push(r);
  });

  var avvik=0, aktive=0, withinTargets=0, hygMet=0, hygTotal=0;
  var yesterday = new Date(today); yesterday.setDate(yesterday.getDate()-1);

  var systems = SYSTEMS.map(function(scfg){
    var recs = bySystem[scfg.id].sort(function(a,b){ return a.date-b.date; });
    if (!recs.length) {
      var empty = {id:scfg.id,name:scfg.name,group:scfg.group,status:"watch",
        updated:"—",temp:null,ph:null,fukt:null,"for":0,targets:scfg.targets,
        tempSeries:{},fuktSeries:{},phSeries:{}};
      RANGES.forEach(function(r){ empty.tempSeries[r.key]=[]; empty.fuktSeries[r.key]=[]; empty.phSeries[r.key]=[]; });
      if (scfg.group==="precompost"){empty.threshold=scfg.threshold;empty.required=scfg.required;empty.dailyLow=[];empty.streak=0;hygTotal++;}
      return empty;
    }

    var last = recs[recs.length-1];
    if (last.date >= yesterday) aktive++;

    var tPairs=[], mPairs=[], pPairs=[];
    recs.forEach(function(r){
      if(r.temp!==null) tPairs.push([r.date, r.temp]);
      if(r.moisture!==null) mPairs.push([r.date, r.moisture]);
      if(r.ph!==null) pPairs.push([r.date, r.ph]);
    });

    var obj = {
      id:scfg.id, name:scfg.name, group:scfg.group,
      updated: fmtDate_(last.date),
      temp: last.temp!==null ? Math.round(last.temp*10)/10 : null,
      ph: last.ph!==null ? Math.round(last.ph*10)/10 : null,
      fukt: last.moisture!==null ? Math.round(last.moisture*10)/10 : null,
      "for": 0,
      targets: scfg.targets,
      tempSeries: buildSeries_(tPairs, today),
      fuktSeries: buildSeries_(mPairs, today),
      phSeries:  buildSeries_(pPairs, today)
    };

    var streak = null;
    if (scfg.group==="precompost") {
      var dl = dailyLow_(tPairs, 10, today);
      streak = computeStreak_(dl, scfg.threshold);
      obj.threshold=scfg.threshold; obj.required=scfg.required;
      obj.dailyLow=dl; obj.streak=streak;
      hygTotal++;
      if (streak>=scfg.required) hygMet++;
    }

    var status = computeStatus_(scfg, {temp:last.temp,moisture:last.moisture,ph:last.ph}, streak);
    obj.status = status;
    if (status==="under") avvik++;
    if (status==="ok") withinTargets++;
    return obj;
  });

  var health = SYSTEMS.length ? Math.round(100*withinTargets/SYSTEMS.length) : 0;

  return {
    RANGES: RANGES.map(function(r){ return {key:r.key,label:r.label,n:r.n>0?r.n:SYSTEMS.length}; }),
    SYSTEMS: systems,
    KPIS: {avvik:avvik, hygienisering:{met:hygMet,total:hygTotal}, aktive:aktive,
      populasjon:0, hosting:health, oppgaver:0,
      omsetning:0, omsetningMaal:100000, omsetningDager:0},
    REMINDERS:[], PROJECTS:[], REGULATORY: buildRegulatory_(systems),
    WEEK:{number:getWeekNumber_(today),title:"Ukens fokus",goal:"",tasks:[],
      metric:{label:"Omsetning mot 100 000-mål",value:0,target:100000}},
    MILESTONES:[], MOTIVATION:[], fmt:{}
  };
}

function buildSeries_(pairs, today) {
  pairs.sort(function(a,b){ return a[0]-b[0]; });
  var out = {};
  var ytdStart = new Date(today.getFullYear(), 0, 1);
  var allStart = pairs.length ? pairs[0][0] : today;

  RANGES.forEach(function(r){
    var cutoff;
    if (r.n===-1) cutoff = ytdStart;
    else if (r.n===-2) cutoff = allStart;
    else cutoff = new Date(today.getTime() - r.n*86400000);

    var dayMap = {};
    pairs.forEach(function(p){ if(p[0]>=cutoff && p[1]!==null) dayMap[p[0].toDateString()]=p[1]; });
    var keys = Object.keys(dayMap).sort();
    out[r.key] = keys.map(function(k){ return Math.round(dayMap[k]*10)/10; });
  });
  return out;
}

function dailyLow_(pairs, nDays, today) {
  var cutoff = new Date(today.getTime() - nDays*86400000);
  var mins = {};
  pairs.forEach(function(p){
    if(p[1]===null || p[0]<cutoff) return;
    var k = p[0].toDateString();
    if(!(k in mins) || p[1]<mins[k]) mins[k]=p[1];
  });
  return Object.keys(mins).sort().map(function(k){ return Math.round(mins[k]*10)/10; });
}

function computeStreak_(dailyLow, threshold) {
  var streak=0;
  for(var i=dailyLow.length-1;i>=0;i--){
    if(dailyLow[i]>=threshold) streak++; else break;
  }
  return streak;
}

function computeStatus_(scfg, latest, streak) {
  if (scfg.group==="precompost") {
    if (streak!==null && streak<scfg.required) return "under";
    if (latest.temp!==null && latest.temp<scfg.threshold) return "under";
  }
  var targets = scfg.targets;
  var checks = [{field:"temp",key:"temp"},{field:"moisture",key:"fukt"},{field:"ph",key:"ph"}];
  for (var i=0;i<checks.length;i++){
    var val = latest[checks[i].field];
    var t = targets[checks[i].key];
    if (val!==null && t && (val<t[0]||val>t[1])) return "watch";
  }
  return "ok";
}

function buildRegulatory_(systems) {
  var items=[];
  systems.forEach(function(s){
    if(s.group!=="precompost") return;
    var ok = s.streak >= s.required;
    items.push({
      id:items.length+1,
      label:"§19 Hygienisering — "+s.name,
      state: ok?"OK":"Avvik",
      tone: ok?"green":"bad",
      detail: ok ? "Streak "+s.streak+" dager ≥ "+s.threshold+" °C"
                 : "Streak "+s.streak+"/"+s.required+" dager over "+s.threshold+" °C"
    });
  });
  return items;
}

function fmtDate_(d) {
  var dd = ("0"+d.getDate()).slice(-2);
  var mm = ("0"+(d.getMonth()+1)).slice(-2);
  return dd+"."+mm+" 00:00";
}

function getWeekNumber_(d) {
  var jan1 = new Date(d.getFullYear(),0,1);
  return Math.ceil(((d-jan1)/86400000+jan1.getDay()+1)/7);
}

// ── GitHub push ─────────────────────────────────────────────────────────────

function pushToGitHub_(jsonContent) {
  var props = PropertiesService.getScriptProperties();
  var token  = props.getProperty("GITHUB_TOKEN");
  var repo   = props.getProperty("REPO") || "martin-starr/verminord-interactive";
  var branch = props.getProperty("BRANCH") || "master";

  if (!token) throw new Error("Sett GITHUB_TOKEN i Script Properties");

  var path = "data.json";
  var apiBase = "https://api.github.com/repos/" + repo + "/contents/" + path;

  // Get current file SHA (for update)
  var sha = null;
  var getResp = UrlFetchApp.fetch(apiBase + "?ref=" + branch, {
    headers: {"Authorization": "Bearer " + token, "Accept": "application/vnd.github.v3+json"},
    muteHttpExceptions: true
  });
  if (getResp.getResponseCode() === 200) {
    sha = JSON.parse(getResp.getContentText()).sha;
  }

  var payload = {
    message: "chore: oppdater data.json fra Google Sheet (" + Utilities.formatDate(new Date(), "Europe/Oslo", "yyyy-MM-dd") + ")",
    content: Utilities.base64Encode(jsonContent, Utilities.Charset.UTF_8),
    branch: branch
  };
  if (sha) payload.sha = sha;

  var putResp = UrlFetchApp.fetch(apiBase, {
    method: "put",
    headers: {"Authorization": "Bearer " + token, "Accept": "application/vnd.github.v3+json"},
    contentType: "application/json",
    payload: JSON.stringify(payload)
  });

  if (putResp.getResponseCode() !== 200 && putResp.getResponseCode() !== 201) {
    throw new Error("GitHub push feilet: " + putResp.getContentText());
  }
  Logger.log("Pushet data.json til GitHub (%s bytes)", jsonContent.length);
}
