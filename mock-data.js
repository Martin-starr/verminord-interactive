/**
 * mock-data.js — Reservedata for Verminord Storskjerm.
 *
 * Brukes kun som fallback dersom fetch('data.json') feiler.
 * Strukturen er identisk med data.json (= window.VN).
 *
 * For live-data: sync_sheet.py genererer data.json fra Google Sheet.
 */

window.VN = {
  RANGES: [
    {key:"7D",label:"7 DGR",n:7},{key:"21D",label:"21 DGR",n:21},
    {key:"3M",label:"3 MND",n:90},{key:"6M",label:"6 MND",n:180},
    {key:"YTD",label:"I ÅR",n:155},{key:"ALL",label:"ALT",n:365}
  ],
  SYSTEMS: [
    {
      id:"cft1",name:"CFT1",group:"prod",status:"ok",
      updated:"03.06 18:26",
      temp:22,ph:7.5,fukt:73,"for":10,
      targets:{temp:[15,25],fukt:[60,80],ph:[6.0,8.0]},
      tempSeries:{
        "7D":[21.3,21.5,22.0,21.8,22.1,22.4,22.0],
        "21D":[20.1,20.3,20.5,20.8,21.0,21.2,21.0,20.9,21.1,21.4,21.6,21.3,21.5,21.8,22.0,21.7,21.9,22.1,21.8,22.0,22.0],
        "3M":[],"6M":[],"YTD":[],"ALL":[]
      },
      fuktSeries:{
        "7D":[72,71,73,74,72,73,73],
        "21D":[70,71,70,72,73,71,72,73,74,73,72,71,72,73,74,72,73,74,73,73,73],
        "3M":[],"6M":[],"YTD":[],"ALL":[]
      },
      phSeries:{
        "7D":[7.4,7.4,7.5,7.5,7.6,7.5,7.5],
        "21D":[7.2,7.3,7.3,7.4,7.4,7.3,7.4,7.4,7.5,7.5,7.4,7.4,7.5,7.5,7.6,7.5,7.5,7.5,7.5,7.5,7.5],
        "3M":[],"6M":[],"YTD":[],"ALL":[]
      }
    },
    {
      id:"cft2",name:"CFT2",group:"prod",status:"ok",
      updated:"03.06 17:45",
      temp:21,ph:7.3,fukt:68,"for":8,
      targets:{temp:[15,25],fukt:[60,80],ph:[6.0,8.0]},
      tempSeries:{"7D":[20.5,20.8,21.0,20.9,21.2,21.0,21.0],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]},
      fuktSeries:{"7D":[67,68,67,69,68,68,68],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]},
      phSeries:{"7D":[7.2,7.3,7.2,7.3,7.3,7.3,7.3],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]}
    },
    {
      id:"cft3",name:"CFT3",group:"prod",status:"watch",
      updated:"03.06 16:10",
      temp:24,ph:7.8,fukt:59,"for":6,
      targets:{temp:[15,25],fukt:[60,80],ph:[6.0,8.0]},
      tempSeries:{"7D":[23.0,23.2,23.5,23.8,24.0,24.2,24.0],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]},
      fuktSeries:{"7D":[63,62,61,60,59,59,59],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]},
      phSeries:{"7D":[7.6,7.7,7.7,7.8,7.8,7.8,7.8],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]}
    },
    {
      id:"wedge1",name:"Wedge 1",group:"prod",status:"ok",
      updated:"03.06 18:00",
      temp:19,ph:7.1,fukt:71,"for":12,
      targets:{temp:[15,25],fukt:[60,80],ph:[6.0,8.0]},
      tempSeries:{"7D":[18.5,18.8,19.0,18.9,19.1,19.0,19.0],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]},
      fuktSeries:{"7D":[70,71,70,72,71,71,71],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]},
      phSeries:{"7D":[7.0,7.1,7.0,7.1,7.1,7.1,7.1],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]}
    },
    {
      id:"wedge2",name:"Wedge 2",group:"prod",status:"ok",
      updated:"03.06 17:30",
      temp:20,ph:7.2,fukt:74,"for":11,
      targets:{temp:[15,25],fukt:[60,80],ph:[6.0,8.0]},
      tempSeries:{"7D":[19.5,19.8,20.0,19.8,20.1,20.0,20.0],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]},
      fuktSeries:{"7D":[73,74,73,75,74,74,74],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]},
      phSeries:{"7D":[7.1,7.2,7.1,7.2,7.2,7.2,7.2],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]}
    },
    {
      id:"breeder",name:"Breeder",group:"prod",status:"ok",
      updated:"03.06 18:15",
      temp:21,ph:7.0,fukt:76,"for":5,
      targets:{temp:[15,25],fukt:[60,80],ph:[6.0,8.0]},
      tempSeries:{"7D":[20.5,20.8,21.0,20.8,21.1,21.0,21.0],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]},
      fuktSeries:{"7D":[75,76,75,77,76,76,76],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]},
      phSeries:{"7D":[6.9,7.0,6.9,7.0,7.0,7.0,7.0],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]}
    },
    {
      id:"forkompost1",name:"Forkompost 1",group:"precompost",status:"ok",
      updated:"03.06 18:30",
      temp:62,ph:7.8,fukt:58,"for":0,
      targets:{temp:[55,80],fukt:[50,70],ph:[6.0,8.5]},
      threshold:55,required:5,
      dailyLow:[58.2,57.5,59.0,60.1,58.8,61.2,59.5,62.0,61.5,62.0],
      streak:10,
      tempSeries:{"7D":[60.5,61.0,60.8,61.5,62.0,61.8,62.0],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]},
      fuktSeries:{"7D":[57,58,57,59,58,58,58],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]},
      phSeries:{"7D":[7.7,7.8,7.7,7.8,7.8,7.8,7.8],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]}
    },
    {
      id:"forkompost2",name:"Forkompost 2",group:"precompost",status:"under",
      updated:"03.06 18:30",
      temp:52,ph:7.6,fukt:61,"for":0,
      targets:{temp:[55,80],fukt:[50,70],ph:[6.0,8.5]},
      threshold:55,required:5,
      dailyLow:[56.0,55.2,54.8,53.5,52.0,51.8,52.5,52.0,52.0,52.0],
      streak:0,
      tempSeries:{"7D":[54.5,54.0,53.5,53.0,52.5,52.0,52.0],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]},
      fuktSeries:{"7D":[60,61,60,62,61,61,61],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]},
      phSeries:{"7D":[7.5,7.6,7.5,7.6,7.6,7.6,7.6],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]}
    }
  ],
  KPIS:{
    avvik:1,
    hygienisering:{met:1,total:2},
    aktive:8,
    populasjon:15936,
    hosting:87.5,
    oppgaver:9,
    omsetning:47200,
    omsetningMaal:100000,
    omsetningDager:9
  },
  REMINDERS:[
    {id:1,tag:"AKUTT",tone:"gold",title:"Forkompost 2 under 55 °C",meta:"Streak brutt — §19 avvik",sub:"Sjekk isolasjon og vending"}
  ],
  PROJECTS:[
    {id:1,name:"Utvidet CFT-kapasitet",status:"I gang",progress:60,value:"↑ 40 % kapasitet",due:"4 dgr",tone:"gold"},
    {id:2,name:"Klasse I-sertifisering",status:"Bestått",progress:100,value:"ALS-rapport klar",due:"—",tone:"green"}
  ],
  REGULATORY:[
    {id:1,label:"§19 Hygienisering — Forkompost 1",state:"OK",tone:"green",detail:"Streak 10 dager ≥ 55 °C"},
    {id:2,label:"§19 Hygienisering — Forkompost 2",state:"Avvik",tone:"bad",detail:"Streak 0/5 dager over 55 °C"}
  ],
  WEEK:{
    number:23,
    title:"Ukens fokus",
    goal:"Rette opp Forkompost 2, forberede neste batch",
    tasks:[
      {t:"Vend FK2, sjekk isolasjon",who:"Habiba",tone:"gold"},
      {t:"Logg alle systemer daglig",who:"Martin",tone:"teal"},
      {t:"Oppdater foto-indeks",who:"Martin",tone:"muted"}
    ],
    metric:{label:"Omsetning mot 100 000-mål",value:47200,target:100000}
  },
  MILESTONES:[
    {title:"15 936 i populasjon",detail:"Ny rekord for anlegget",tone:"green",icon:"▲"},
    {title:"Klasse I oppnådd",detail:"ALS Lab NO2604972",tone:"green",icon:"✓"}
  ],
  MOTIVATION:[
    {tag:"UKENS MÅL",text:"350 / 500 poser solgt · 16 dager igjen — stå på!"}
  ],
  fmt:{}
};
