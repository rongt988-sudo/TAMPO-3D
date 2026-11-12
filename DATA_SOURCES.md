# Public source datasets

The following public products underpin the TAMPO-3D study. Study domain: **120–135°E, 18–29°N**. Product identifiers and study coverage are documented below; the downloadable provider products are distinct from the final plotting variables included in this repository.

Catalogue checked on **2026-11-13**. This is the documentation/access-check date. Original acquisition dates are not recorded in the available acquisition records. The accompanying [CSV catalogue](DATA_SOURCES.csv) includes dataset identifiers, versions, coverage, access conditions, and provider links.

| Product | Variables and native sampling | Version / product ID | Study coverage | Source and citation |
| --- | --- | --- | --- | --- |
| GLORYS12V1 | thetao; so; uo; vo; 1/12 degree; daily; 50 native depth levels | GLORYS12V1; `GLOBAL_MULTIYEAR_PHY_001_030` | 2013–2023 (manuscript source coverage); 33 retained levels, 0.494–643.567 m | [Provider](https://data.marine.copernicus.eu/product/GLOBAL_MULTIYEAR_PHY_001_030/description); [DOI](https://doi.org/10.48670/moi-00021) |
| MUR SST | analysed_sst; 0.01 degree; daily | 4.1 (local metadata: 04.1); `MUR-JPL-L4-GLOB-v4.1` | 2013–2023 (manuscript source coverage) | [Provider](https://podaac.jpl.nasa.gov/dataset/MUR-JPL-L4-GLOB-v4.1); [DOI](https://doi.org/10.5067/GHGMR-4FJ04) |
| Sea surface salinity | sos; 0.125 degree; daily | Multi-observation daily reprocessed product; dataset identifier as in local files; `MULTIOBS_GLO_PHY_S_SURFACE_MYNRT_015_013` | 2013–2023 (manuscript source coverage) | [Provider](https://data.marine.copernicus.eu/product/MULTIOBS_GLO_PHY_S_SURFACE_MYNRT_015_013/description); [DOI](https://doi.org/10.48670/moi-00051) |
| DUACS sea level anomaly | sla; 0.125 degree; daily | Delayed-time multi-satellite L4 DUACS; dataset identifier as in local files; `SEALEVEL_GLO_PHY_L4_MY_008_047` | 2013–2023 (manuscript source coverage) | [Provider](https://data.marine.copernicus.eu/product/SEALEVEL_GLO_PHY_L4_MY_008_047/description); [DOI](https://doi.org/10.48670/moi-00148) |
| CCMP winds | 10 m zonal and meridional winds; derived wind-stress curl; 0.25 degree; 6-hourly, aggregated to daily for the study | V3.1 (manuscript product specification); `CCMP` | 2013–2023 (manuscript source coverage) | [Provider](https://www.remss.com/measurements/ccmp/); Provider product documentation |
| Argo profiles | temperature; salinity; profile location and time; Individual profiles; irregular spatial and temporal sampling | Profile files from GDAC; individual profile identifiers retained in the shared data; `Argo GDAC` | 2023 observational validation and profile cases | [Provider](https://data-argo.ifremer.fr/); [DOI](https://doi.org/10.17882/42182) |
| ETOPO2022 | surface elevation / bathymetry; 60 arc-second local grid; provider also distributes 15 and 30 arc-second grids | ETOPO 2022 v1; local surface-elevation input: 60 arc-second grid; `ETOPO 2022 Global Relief Model` | Static topography and bathymetry | [Provider](https://www.ncei.noaa.gov/products/etopo-global-relief-model); [DOI](https://doi.org/10.25921/fd45-gt74) |
| META4.0 DT | eddy trajectories; centres; contours; polarity; Daily eddy observations and trajectories | 4.0 delayed-time all-satellite product; `Mesoscale Eddy Trajectory Atlas META4.0 DT` | Local atlas: 1993-01-01–2023-09-08; study cases within 2023 coverage | [Provider](https://www.aviso.altimetry.fr/fr/donnees/produits/produits-a-valeur-ajoutee/trajectoires-de-tourbillons-mesoechelles.html); [DOI](https://doi.org/10.24400/527896/a01-2026.001) |

## Access and attribution

- **GLORYS12V1, sea surface salinity, and DUACS SLA:** access through the Copernicus Marine product pages and their Data access tabs. Cite the product DOI listed above and acknowledge Copernicus Marine Service.
- **MUR SST:** access through NASA/JPL PO.DAAC, or the [NOAA CoastWatch ERDDAP mirror](https://coastwatch.pfeg.noaa.gov/erddap/griddap/jplMURSST41). Cite MUR-JPL-L4-GLOB-v4.1 and its dataset DOI.
- **CCMP:** follow the Remote Sensing Systems product documentation and [FTP registration](https://register.remss.com/). Acknowledge Remote Sensing Systems and identify V3.1 when citing the study’s specified product.
- **Argo:** access profiles from the public [GDAC](https://data-argo.ifremer.fr/). Cite the Argo dataset DOI and acknowledge the international Argo program and contributing national programs.
- **ETOPO2022:** access NOAA NCEI’s Global Relief Model page. The local input is identified by the 60 arc-second surface-grid filename in the CSV catalogue. Cite NOAA NCEI (2022), ETOPO 2022, DOI 10.25921/fd45-gt74.
- **META4.0 DT:** access the AVISO+ mesoscale eddy trajectory catalogue. Cite the META4.0 DT dataset DOI and acknowledge CLS/CNES/AVISO+.

Native provider grids and sampling differ among products. The final plotting variables, masks, and coordinates needed by the drawing scripts are already supplied in `data/`.
