const cookieTypes = {
  cookies_policy: "essential",
  cookies_preferences_set: "essential",
  _ga: "usage",
  _gid: "usage",
  _gat: "usage",
};



export function showCookieBannerIfNotSetAndSetTrackingCookies(){
  if(window.gaMeasurementId){
    cookieTypes[`_ga_${window.gaMeasurementId}`] = 'usage';
  }

  showCookieBanner()
  if (getCookie('cookies_preferences_set')) {
    hideCookieBanner()
  }

  setTrackingCookies()
}

export function deleteCookie (name) {
  document.cookie = name + "=;expires=" + new Date + ";domain=" + window.location.hostname + ";path=/";
}

export function setCookie (name, value, days) {
  var expires = ''
  if (days) {
    var date = new Date()
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000))
    expires = '; expires=' + date.toUTCString()
  }
  document.cookie = name + '=' + (value || '') + expires + '; path=/'
}

export function getCookie (name) {
  var nameEQ = name + '='
  var ca = document.cookie.split(';')
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i]
    while (c.charAt(0) === ' ') c = c.substring(1, c.length)
    if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length)
  }
  return null
}

export function acceptCookies (cookiePrefs = { essential: true, settings: true, usage: true, campaigns: true }) { // eslint-disable-line no-unused-vars
  setCookie('cookies_preferences_set', true, 365)
  setCookie('cookies_policy', JSON.stringify(cookiePrefs), 365)
  hideCookieBanner()
  showCookieConfirmation()
  setTrackingCookies()
}

export function hideCookieBanner () {
  var cookieBanner = document.getElementById('cookie-banner')
  if(cookieBanner){
    cookieBanner.style.display = 'none'
    cookieBanner.ariaHidden = true
  }
}

export function showCookieBanner () {
  var cookieBanner = document.getElementById('cookie-banner')
  if(cookieBanner){
    cookieBanner.style.display = 'block'
    cookieBanner.ariaHidden = false
  }
}

export function hideCookieConfirmation () {
  hideCookieBanner ()
  var cookieBanner = document.getElementById('cookie-confirmation')
  if(cookieBanner){
    cookieBanner.style.display = 'none'
    cookieBanner.ariaHidden = true
  }
}

export function showCookieConfirmation () {
  var cookieBanner = document.getElementById('cookie-confirmation')
  if(cookieBanner){
    cookieBanner.style.display = 'block'
    cookieBanner.ariaHidden = false
  }
}

export function setTrackingCookies () {
  var cookiesPolicy = JSON.parse(getCookie('cookies_policy'))
  var doNotTrack = cookiesPolicy == null || !cookiesPolicy.usage
  if (doNotTrack) {
    if(window.gaMeasurementId){
      window[`ga-disable-${window.gaMeasurementId}`] = true;
    }
  } else {
    if(window.gaMeasurementId){
      window.dataLayer = window.dataLayer || [];
      window.gtag = function(){dataLayer.push(arguments);}
      window.gtag('js', new Date());
      window.gtag('config', window.gaMeasurementId);
      window[`ga-disable-${window.gaMeasurementId}`] = false;
    } else {
      console.warn('Google Analytics: No measurement ID specified');
    }

    /* Smartlook */
    if (window.smartlookId && window.smartlookId !== 'None') {
      initialiseSmartlook();
    }
  }
}

function initialiseSmartlook() {
  const smartLookPromise = new Promise((resolve) => {
    if (typeof window.smartlook === 'function') {
      resolve();
      return;
    }

    window.smartlook||(function(d) {
      var o=window.smartlook=function(){ o.api.push(arguments)},h=d.getElementsByTagName('head')[0];
      var c=d.createElement('script');o.api=new Array();c.async=true;c.type='text/javascript';
      c.charset='utf-8';c.src='https://web-sdk.smartlook.com/recorder.js';h.appendChild(c);
    })(document);

    // Wait for the script to load and check if smartlook is available
    setTimeout(() => {
      if (typeof window.smartlook !== 'function') {
        console.warn('Smartlook: Failed to load the script');
      } else {
        resolve();
      }
    }, 2000);
  });

  smartLookPromise.then(() => {
    window.smartlook("init", window.smartlookId, {
      region: "eu"
    });

    window.smartlook("record", {
      forms: true,
      ips: false,
      emails: false,
      numbers: true
    });
  });
}

export class cookiePrefs{
  static essential = true;
  static settings = false;
  static usage = false;
  static campaigns = false;

  static get = () => {
    var cookiesPolicy = JSON.parse(getCookie('cookies_policy'));
    if(cookiesPolicy){
      this.setEssential(cookiesPolicy.essential);
      this.setSettings(cookiesPolicy.settings);
      this.setUsage(cookiesPolicy.usage);
      this.setCampaigns(cookiesPolicy.campaigns);
    }
  }

  static setEssential = (value) => this.essential = value;
  static setSettings = (value) => this.settings = value;
  static setUsage = (value) => this.usage = value;
  static setCampaigns = (value) => this.campaigns = value;

  static save = (expires = 365) => {
    setCookie('cookies_preferences_set', true, expires)
    setCookie('cookies_policy', JSON.stringify({
      essential: this.essential,
      settings: this.settings,
      usage: this.usage,
      campaigns: this.campaigns
    }), expires)
    hideCookieBanner()
    this.invalidateRejectedCookies()
    setTrackingCookies()
  }

  static invalidateRejectedCookies = () => {
    for (const name in cookieTypes){
      if(!this.essential && cookieTypes[name] == 'essential'){
        deleteCookie(name);
      }
      if(!this.settings && cookieTypes[name] == 'settings'){
        deleteCookie(name);
      }
      if(!this.usage && cookieTypes[name] == 'usage'){
        deleteCookie(name);
      }
      if(!this.campaigns && cookieTypes[name] == 'campaigns'){
        deleteCookie(name);
      }
    }
  }
}
