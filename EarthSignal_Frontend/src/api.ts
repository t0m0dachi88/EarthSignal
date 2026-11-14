export const VARIABLES = [
 {id:'air_temperature_c',name:'Air temperature',short:'Air temp',unit:'°C'},
 {id:'surface_temperature_c',name:'Surface temperature',short:'Surface temp',unit:'°C'},
 {id:'precipitation_mm_month',name:'Precipitation',short:'Precipitation',unit:'mm/month'},
 {id:'evapotranspiration_mm_month',name:'Evapotranspiration',short:'Evapotranspiration',unit:'mm/month'},
 {id:'topsoil_water_kg_m2',name:'Topsoil water',short:'Topsoil water',unit:'kg/m²'},
 {id:'rootzone_water_kg_m2',name:'Rootzone water',short:'Rootzone water',unit:'kg/m²'},
];
export type Discovery = {target_variable:string;cell_a:number;cell_b:number;lat_a:number;lon_a:number;lat_b:number;lon_b:number;target_slope_a:number;target_slope_b:number;target_difference:number;separation_km:number;contrast_score:number;fdr_significant?:boolean;fdr_q_value?:number;spatial_eligible_primary?:boolean;direction_persistent?:boolean;integrated_candidate_flag?:boolean;cluster_a?:number;cluster_b?:number;[key:string]:unknown};
export type DiscoveryResponse={items:Discovery[];total:number;offset:number;limit:number};
export type Trend={variable:string;units:string;location:{latitude:number;longitude:number;cell_id?:number};time_series:{year:number;anomaly:number|null}[];trend:{classification:string;slope_per_decade:number|null;p_value_uncorrected:number|null;confidence_interval_95_per_decade:number[]|null;observation_count:number};period:{start_year:number;end_year:number}};
export type MLHealth={ready:boolean;cells:number;discoveries:number;clusters:number;error:string|null};
const BASE=(import.meta.env.VITE_API_BASE_URL || '/api').replace(/\/$/,'');
export async function api<T>(path:string,options:RequestInit={}):Promise<T>{
 const token=localStorage.getItem('earthsignal_token');
 const headers:Record<string,string>={'Content-Type':'application/json',...(options.headers as Record<string,string>||{})};
 if(token)headers.Authorization=`Bearer ${token}`;
 let response:Response;
 try{response=await fetch(`${BASE}${path}`,{...options,headers});}catch{throw new Error('Cannot reach EarthSignal API. Start FastAPI on port 8000.');}
 if(!response.ok){let message=`API error ${response.status}`;try{const body=await response.json();message=typeof body.detail==='string'?body.detail:JSON.stringify(body.detail||body);}catch{}throw new Error(message);}
 return response.json() as Promise<T>;
}
export function fmt(n:number|null|undefined,digits=1){return typeof n==='number'&&Number.isFinite(n)?n.toLocaleString('en-US',{maximumFractionDigits:digits}):'—';}
export function variableName(id:string){return VARIABLES.find(v=>v.id===id)?.name||id;}
export function slug(id:string){return id.replace(/_/g,' ');}
