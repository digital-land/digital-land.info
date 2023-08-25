export function goBack(href) {
    const originLength = document.location.origin.length;
    const originAndPathLength = document.location.origin.length + document.location.pathname.length;
    const subPath = document.referrer.substring(originLength, originAndPathLength);
    if(subPath === href) {
        window.history.back();
        return false;
    }
    return true;
}
