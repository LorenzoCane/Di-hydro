# Di-hydro - Data download

In this repo I put together a bunch of scripts that I have used in the preliminary phase (data searching and acquisition) of a bigger project about ML prevision model of rivers levels using satellites data. 

Using the following scripts it is possible to download data from the ERA5 dataset and from the [METEOS Elektromorava dataset](http://www.meteos.rs/ahs/elektromorava/).

The CDS API download code use access based on **CDS API personal access token**. If you haven't yet set it up please follow the [Copernicus page instructions](https://cds.climate.copernicus.eu/how-to-api).
If you don't have a **Copernicus account**, please register yourself in the [Copernicus page](https://accounts.ecmwf.int/auth/realms/ecmwf/protocol/openid-connect/auth?client_id=cds&scope=openid%20email&response_type=code&redirect_uri=https%3A%2F%2Fcds.climate.copernicus.eu%2Fapi%2Fauth%2Fcallback%2Fkeycloak&state=1Dmc7R8xfXzErvruclyu5G3abQLAbDVba-1qV8jtCyM&code_challenge=Fsa09MEpA-Rgtrc1MlTnYflPtGUEqATVMDss8iQMkuA&code_challenge_method=S256) and then login.