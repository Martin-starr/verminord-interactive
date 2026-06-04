/**
 * mock-data.js — Reservedata for Verminord Storskjerm.
 *
 * Brukes kun som fallback dersom fetch('data.json') feiler.
 * Strukturen er identisk med data.json (= window.VN).
 *
 * For live-data: sync_sheet.py genererer data.json fra Google Sheet.
 * Lengre tidsserier (6M, YTD, ALL) er forkortet til siste 7 verdier.
 */

window.VN = {
  RANGES: [
    {key:"7D",label:"7 DGR",n:7},{key:"21D",label:"21 DGR",n:21},
    {key:"3M",label:"3 MND",n:90},{key:"6M",label:"6 MND",n:180},
    {key:"YTD",label:"I ÅR",n:154},{key:"ALL",label:"ALT",n:332}
  ],
  SYSTEMS: [
    {
      id:"cft1",name:"CFT1",group:"prod",status:"ok",
      updated:"03.06 18:26",
      temp:22,ph:7.5,fukt:73,"for":10,
      targets:{temp:[15,25],fukt:[60,85],ph:[6.0,8.0]},
      tempSeries:{
        "7D":[21.0,22.0,19.0],
        "21D":[20.3,20.8,25.0,24.0,16.8,21.0,22.0,19.0],
        "3M":[14.0,16.0,18.0,18.0,17.0,17.0,17.0,18.0,17.0,19.0,17.0,19.0,18.0,19.0,16.0,22.0,22.0,20.5,18.0,19.4,20.3,20.8,25.0,24.0,16.8,21.0,22.0,19.0],
        "6M":[20.3,20.8,25.0,24.0,16.8,21.0,19.0],
        "YTD":[20.3,20.8,25.0,24.0,16.8,21.0,22.0,19.0],
        "ALL":[20.3,20.8,25.0,24.0,16.8,21.0,22.0,19.0]
      },
      fuktSeries:{
        "7D":[63.0,75.0,64.0],
        "21D":[68.0,74.0,74.0,83.0,65.0,63.0,75.0,64.0],
        "3M":[76.0,77.0,78.0,80.0,70.0,76.0,74.0,75.0,80.0,83.0,77.0,82.0,64.0,75.0,78.0,64.0,60.0,75.0,84.0,60.0,68.0,74.0,74.0,83.0,65.0,63.0,75.0,64.0],
        "6M":[74.0,74.0,83.0,65.0,63.0,75.0,64.0],
        "YTD":[74.0,74.0,83.0,65.0,63.0,75.0,64.0],
        "ALL":[74.0,74.0,83.0,65.0,63.0,75.0,64.0]
      },
      phSeries:{
        "7D":[7.2,7.5,7.5],
        "21D":[7.5,7.5,7.5,7.3,7.4,7.2,7.5,7.5],
        "3M":[7.0,6.5,6.0,6.5,7.0,7.5,7.5,7.5,6.5,6.5,6.0,6.0,7.5,7.5,7.5,7.5,7.5,7.5,7.5,7.5,7.5,7.5,7.5,7.3,7.4,7.2,7.5,7.5],
        "6M":[7.5,7.5,7.3,7.4,7.2,7.5,7.5],
        "YTD":[7.5,7.5,7.3,7.4,7.2,7.5,7.5],
        "ALL":[7.5,7.5,7.3,7.4,7.2,7.5,7.5]
      }
    },
    {
      id:"cft2",name:"CFT2",group:"prod",status:"ok",
      updated:"03.06 18:22",
      temp:24,ph:7.5,fukt:76,"for":10,
      targets:{temp:[15,25],fukt:[60,85],ph:[6.0,8.0]},
      tempSeries:{
        "7D":[22.0,24.0],
        "21D":[20.4,21.8,28.0,19.0,20.6,22.0,24.0],
        "3M":[14.0,15.0,15.0,17.0,17.0,16.0,17.0,18.0,18.0,12.0,15.0,18.0,18.0,18.0,17.0,21.0,19.4,26.6,28.0,23.3,20.4,21.8,28.0,19.0,20.6,22.0,24.0],
        "6M":[20.4,21.8,28.0,19.0,20.6,22.0,24.0],
        "YTD":[20.4,21.8,28.0,19.0,20.6,22.0,24.0],
        "ALL":[20.4,21.8,28.0,19.0,20.6,22.0,24.0]
      },
      fuktSeries:{
        "7D":[68.0,76.0],
        "21D":[72.0,74.0,78.0,68.0,60.0,68.0,76.0],
        "3M":[76.0,76.0,76.0,76.0,74.0,76.0,76.0,76.0,63.0,83.0,72.0,74.0,75.0,74.0,72.0,64.0,80.0,74.0,78.0,70.0,72.0,74.0,78.0,68.0,60.0,68.0,76.0],
        "6M":[72.0,74.0,78.0,68.0,60.0,68.0,76.0],
        "YTD":[72.0,74.0,78.0,68.0,60.0,68.0,76.0],
        "ALL":[72.0,74.0,78.0,68.0,60.0,68.0,76.0]
      },
      phSeries:{
        "7D":[7.5,7.5],
        "21D":[7.2,7.5,7.5,7.3,7.3,7.5,7.5],
        "3M":[7.0,6.0,6.0,6.0,7.0,7.5,7.5,7.5,7.0,6.5,6.0,6.0,7.5,7.5,7.5,7.0,7.5,7.5,7.5,7.5,7.2,7.5,7.5,7.3,7.3,7.5,7.5],
        "6M":[7.2,7.5,7.5,7.3,7.3,7.5,7.5],
        "YTD":[7.2,7.5,7.5,7.3,7.3,7.5,7.5],
        "ALL":[7.2,7.5,7.5,7.3,7.3,7.5,7.5]
      }
    },
    {
      id:"cft3",name:"CFT3",group:"prod",status:"ok",
      updated:"03.06 00:16",
      temp:22,ph:7.0,fukt:75,"for":2,
      targets:{temp:[15,25],fukt:[60,85],ph:[6.0,8.0]},
      tempSeries:{
        "7D":[22.0],
        "21D":[22.0],
        "3M":[22.0],
        "6M":[22.0],
        "YTD":[22.0],
        "ALL":[22.0]
      },
      fuktSeries:{
        "7D":[75.0],
        "21D":[75.0],
        "3M":[75.0],
        "6M":[75.0],
        "YTD":[75.0],
        "ALL":[75.0]
      },
      phSeries:{
        "7D":[7.0],
        "21D":[7.0],
        "3M":[7.0],
        "6M":[7.0],
        "YTD":[7.0],
        "ALL":[7.0]
      }
    },
    {
      id:"wedge1",name:"Wedge 1",group:"prod",status:"ok",
      updated:"03.06 18:10",
      temp:23,ph:7.5,fukt:63,"for":0,
      targets:{temp:[15,25],fukt:[60,85],ph:[6.0,8.0]},
      tempSeries:{
        "7D":[23.0],
        "21D":[23.0],
        "3M":[25.0,23.0],
        "6M":[25.0,23.0],
        "YTD":[25.0,23.0],
        "ALL":[20.0,19.0,14.0,19.0,20.0,20.0,20.0,25.0,23.0]
      },
      fuktSeries:{
        "7D":[63.0],
        "21D":[63.0],
        "3M":[71.0,63.0],
        "6M":[71.0,63.0],
        "YTD":[71.0,63.0],
        "ALL":[72.0,52.0,57.0,61.0,60.0,71.0,63.0]
      },
      phSeries:{
        "7D":[7.5],
        "21D":[7.5],
        "3M":[7.5,7.5],
        "6M":[7.5,7.5],
        "YTD":[7.5,7.5],
        "ALL":[5.0,6.0,5.5,7.8,7.0,7.5,7.5]
      }
    },
    {
      id:"wedge2",name:"Wedge 2",group:"prod",status:"ok",
      updated:"03.06 18:12",
      temp:21,ph:7.5,fukt:62,"for":0,
      targets:{temp:[15,25],fukt:[60,85],ph:[6.0,8.0]},
      tempSeries:{
        "7D":[21.0],
        "21D":[21.0],
        "3M":[21.0],
        "6M":[21.0],
        "YTD":[21.0],
        "ALL":[14.0,17.0,18.0,19.0,19.0,19.0,14.0,17.0,21.0]
      },
      fuktSeries:{
        "7D":[62.0],
        "21D":[62.0],
        "3M":[62.0],
        "6M":[62.0],
        "YTD":[62.0],
        "ALL":[61.0,65.0,71.0,77.0,75.0,86.0,60.0,62.0]
      },
      phSeries:{
        "7D":[7.5],
        "21D":[7.5],
        "3M":[7.5],
        "6M":[7.5],
        "YTD":[7.5],
        "ALL":[8.0,7.5,6.5,7.0,5.0,6.0,7.5]
      }
    },
    {
      id:"breeder",name:"Breeder Bin",group:"prod",status:"ok",
      updated:"03.06 18:22",
      temp:23,ph:7.5,fukt:73,"for":10,
      targets:{temp:[15,25],fukt:[60,85],ph:[6.0,8.0]},
      tempSeries:{
        "7D":[23.0],
        "21D":[18.0,23.0],
        "3M":[24.0,18.0,23.0],
        "6M":[24.0,18.0,23.0],
        "YTD":[24.0,18.0,23.0],
        "ALL":[24.0,18.0,23.0]
      },
      fuktSeries:{
        "7D":[73.0],
        "21D":[74.0,73.0],
        "3M":[65.0,74.0,73.0],
        "6M":[65.0,74.0,73.0],
        "YTD":[65.0,74.0,73.0],
        "ALL":[65.0,74.0,73.0]
      },
      phSeries:{
        "7D":[7.5],
        "21D":[7.0,7.5],
        "3M":[7.5,7.0,7.5],
        "6M":[7.5,7.0,7.5],
        "YTD":[7.5,7.0,7.5],
        "ALL":[7.5,7.0,7.5]
      }
    },
    {
      id:"forkompost1",name:"Forkompost 1",group:"precompost",status:"under",
      updated:"03.06 00:50",
      temp:33,ph:7.5,fukt:77,"for":0,
      targets:{temp:[55,80],fukt:[50,70],ph:[6.0,8.5]},
      threshold:55,required:5,
      dailyLow:[33.0],
      streak:0,
      tempSeries:{
        "7D":[33.0],
        "21D":[33.0],
        "3M":[16.0,31.0,24.0,24.0,19.0,16.0,17.0,17.0,59.0,56.0,17.0,16.0,36.0,28.0,17.0,16.0,13.0,17.0,19.0,9.0,16.0,22.0,26.0,24.0,21.0,25.0,21.0,19.0,16.3,20.0,33.0],
        "6M":[25.0,21.0,19.0,16.3,20.0,33.0],
        "YTD":[25.0,21.0,19.0,16.3,20.0,33.0],
        "ALL":[25.0,21.0,19.0,16.3,20.0,33.0]
      },
      fuktSeries:{
        "7D":[77.0],
        "21D":[77.0],
        "3M":[73.0,74.0,74.0,79.0,69.0,70.0,81.0,66.0,70.0,75.0,76.0,67.0,77.0,83.0,73.0,71.0,75.0,64.0,75.0,64.0,78.0,64.0,64.0,79.0,61.0,61.0,65.0,74.0,74.0,70.0,77.0],
        "6M":[61.0,65.0,74.0,74.0,70.0,77.0],
        "YTD":[61.0,65.0,74.0,74.0,70.0,77.0],
        "ALL":[61.0,65.0,74.0,74.0,70.0,77.0]
      },
      phSeries:{
        "7D":[7.5],
        "21D":[7.5],
        "3M":[7.0,6.5,7.4,7.4,7.0,7.0,7.5,7.5,6.5,6.5,6.0,7.6,6.6,7.2,8.0,7.2,6.9,7.5,7.5,7.4,7.5,7.5,7.5,7.5,7.5,7.0,7.5,7.5,7.5,7.0,7.5],
        "6M":[7.0,7.5,7.5,7.5,7.0,7.5],
        "YTD":[7.0,7.5,7.5,7.5,7.0,7.5],
        "ALL":[7.0,7.5,7.5,7.5,7.0,7.5]
      }
    },
    {
      id:"forkompost2",name:"Forkompost 2",group:"precompost",status:"watch",
      updated:"—",
      temp:null,ph:null,fukt:null,"for":0,
      targets:{temp:[55,80],fukt:[50,70],ph:[6.0,8.5]},
      threshold:55,required:5,
      dailyLow:[],
      streak:0,
      tempSeries:{
        "7D":[],
        "21D":[],
        "3M":[19.0,17.0,17.0,34.0,38.0,40.0,46.0,17.0,43.0,19.0,13.0,18.0,8.0,17.0,8.0,18.0,18.0,8.0,17.0,24.0,25.0,25.0,25.0,24.0,18.0,18.0,17.3,22.0],
        "6M":[24.0,18.0,18.0,17.3,22.0],
        "YTD":[24.0,18.0,18.0,17.3,22.0],
        "ALL":[24.0,18.0,18.0,17.3,22.0]
      },
      fuktSeries:{
        "7D":[],
        "21D":[],
        "3M":[72.0,68.0,70.0,80.0,69.0,75.0,76.0,68.0,76.0,75.0,82.0,80.0,82.0,62.0,74.0,56.0,75.0,74.0,62.0,72.0,66.0,74.0,74.0,68.0,65.0,78.0,64.0,70.0,74.0],
        "6M":[65.0,78.0,64.0,70.0,74.0],
        "YTD":[65.0,78.0,64.0,70.0,74.0],
        "ALL":[65.0,78.0,64.0,70.0,74.0]
      },
      phSeries:{
        "7D":[],
        "21D":[],
        "3M":[8.0,6.0,7.5,6.5,6.5,7.1,6.8,6.5,7.0,5.5,7.0,7.5,7.0,7.5,7.2,7.0,7.5,7.5,7.3,7.5,7.2,7.0,7.5,7.0,7.5,7.3,7.5,7.5,7.0],
        "6M":[7.0,7.5,7.3,7.5,7.5,7.0],
        "YTD":[7.0,7.5,7.3,7.5,7.5,7.0],
        "ALL":[7.0,7.5,7.3,7.5,7.5,7.0]
      }
    },
    {
      id:"forkompost3",name:"Forkompost 3",group:"precompost",status:"watch",
      updated:"—",
      temp:null,ph:null,fukt:null,"for":0,
      targets:{temp:[55,80],fukt:[50,70],ph:[6.0,8.5]},
      threshold:55,required:5,
      dailyLow:[],
      streak:0,
      tempSeries:{
        "7D":[],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]
      },
      fuktSeries:{
        "7D":[],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]
      },
      phSeries:{
        "7D":[],"21D":[],"3M":[],"6M":[],"YTD":[],"ALL":[]
      }
    }
  ],
  KPIS:{
    avvik:1,
    hygienisering:{met:0,total:3},
    aktive:7,
    populasjon:15936,
    hosting:67,
    oppgaver:9,
    omsetning:47200,
    omsetningMaal:100000,
    omsetningDager:9
  },
  REMINDERS:[
    {id:1,tag:"AKUTT",tone:"gold",title:"Forkompost 1 under 55 °C",meta:"Siste: 33 °C — streak nullstilt",sub:"Sjekk isolasjon og vending"}
  ],
  PROJECTS:[
    {id:1,name:"Utvidet CFT-kapasitet",status:"I gang",progress:60,value:"↑ 40 % kapasitet",due:"4 dgr",tone:"gold"},
    {id:2,name:"Klasse I-sertifisering",status:"Bestått",progress:100,value:"ALS-rapport klar",due:"—",tone:"green"}
  ],
  REGULATORY:[
    {id:1,label:"§19 Hygienisering — Forkompost 1",state:"Avvik",tone:"bad",detail:"Streak 0/5 dager over 55 °C"},
    {id:2,label:"§19 Hygienisering — Forkompost 2",state:"Ingen data",tone:"muted",detail:"Ingen logg ennå"},
    {id:3,label:"§19 Hygienisering — Forkompost 3",state:"Ingen data",tone:"muted",detail:"Ingen logg ennå"}
  ],
  WEEK:{
    number:23,
    title:"Ukens fokus",
    goal:"Rette opp Forkompost 1, forberede neste batch",
    tasks:[
      {t:"Vend FK1, sjekk isolasjon",who:"Habiba",tone:"gold"},
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
