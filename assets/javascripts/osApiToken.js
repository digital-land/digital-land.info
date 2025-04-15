let apiToken = {
    access_token: '',
    expires_in: 0,
    issued_at: 0
};

let makingRequest = false;


export const getApiToken = () => {
    const tokenCheckBuffer = 30 * 1000;
    const tokenExpires = parseInt(apiToken.expires_in) * 1000 + parseInt(apiToken.issued_at);
    if(Date.now() > tokenExpires - tokenCheckBuffer && !makingRequest){
        getFreshApiToken();
    }
    return apiToken.access_token;
}

export const getFreshApiToken = () => {
    return new Promise((resolve, reject) => {
        makingRequest = true;
        fetch("/os/getToken?cacheBust=" + Date.now())
          .then((res) => res.json())
          .then((res) => {
            apiToken = res;
            makingRequest = false;
            resolve(apiToken.access_token);
          });
    });
}
