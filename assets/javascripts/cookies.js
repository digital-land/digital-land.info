const cookieTypes = {
  cookies_policy: "essential",
  cookies_preferences_set: "essential",
  _ga: "usage",
  _gid: "usage",
  _gat: "usage",
};

if(window.gaMeasurementId){
  cookieTypes[`_ga_${window.gaMeasurementId}`] = 'usage';
}

function deleteCookie (name) {
  document.cookie = name + "=;expires=" + new Date + ";domain=" + window.location.hostname + ";path=/";
}

function setCookie (name, value, days) {
  var expires = ''
  if (days) {
    var date = new Date()
    date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000))
    expires = '; expires=' + date.toUTCString()
  }
  document.cookie = name + '=' + (value || '') + expires + '; path=/'
}

function getCookie (name) {
  var nameEQ = name + '='
  var ca = document.cookie.split(';')
  for (var i = 0; i < ca.length; i++) {
    var c = ca[i]
    while (c.charAt(0) === ' ') c = c.substring(1, c.length)
    if (c.indexOf(nameEQ) === 0) return c.substring(nameEQ.length, c.length)
  }
  return null
}

function acceptCookies (cookiePrefs = { essential: true, settings: true, usage: true, campaigns: true }) { // eslint-disable-line no-unused-vars
  setCookie('cookies_preferences_set', true, 365)
  setCookie('cookies_policy', JSON.stringify(cookiePrefs), 365)
  hideCookieBanner()
  showCookieConfirmation()
  setTrackingCookies()
}

function hideCookieBanner () {
  var cookieBanner = document.getElementById('cookie-banner')
  if(cookieBanner){
    cookieBanner.style.display = 'none'
  }
}

function hideCookieConfirmation () {
  hideCookieBanner ()
  var cookieBanner = document.getElementById('cookie-confirmation')
  if(cookieBanner){
    cookieBanner.style.display = 'none'
  }
}

function showCookieConfirmation () {
  var cookieBanner = document.getElementById('cookie-confirmation')
  if(cookieBanner){
    cookieBanner.style.display = 'block'
  }
}

function setTrackingCookies () {
  var cookiesPolicy = JSON.parse(getCookie('cookies_policy'))
  var doNotTrack = cookiesPolicy == null || !cookiesPolicy.usage
  if (doNotTrack) {
    if(window.gaMeasurementId){
      window[`ga-disable-${window.gaMeasurementId}`] = true;
    }
  } else {
    if(window.gaMeasurementId){
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', window.gaMeasurementId);
    } else {
      console.warn('Google Analytics: No measurement ID specified');
    }
  }
}

class cookiePrefs{
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


if (getCookie('cookies_preferences_set')) {
  hideCookieBanner()
}

setTrackingCookies()
