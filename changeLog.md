<!--
    # Template
    ## [Version(optional)] - [Date]
    ### What's new
    - [Feature]
    - [BugFix]
    - ...
    ### Why was this change made?
    - [explanation]
    ***
    <br />
-->

# ChangeLog
<br>

## 10-10-2023
### What's new
- Added an acceptance test that tests navigation to a dataset page
### Why was this change made?
- because this user journey was documented as part of a recent group session we did

## 09-10-2023
### What's new
- Added tests to ensure each and every page request returns a successful response
- Refactored the tests to remove duplicate code
### Why was this change made?
- To ensure we don't introduce any broken pages to the live site

## 06-10-2023
### What's new
- entities filter renamed to period
- period filter now uses checkboxes
- period filter clear now works as expected
- period value (historical/current) now indicated on the entity
### Why was this change made?
- To ensure user don't mistake historical entities for current entities

## 03-10-2023
### What's new
- Fixed the layer controls component for safari, as the checkboxes were not changing state
### Why was this change made?
- So the layer controls work on safari

## 29-09-2023
### What's new
- Updated the rendering of a polygon layer to also check for point data and render a circle where appropriate
### Why was this change made?
- to handle the new NSIP dataset

## 29-09-2023
### What's new
- Setup axe playwright accessibility testing for all pages
- Fixed any issues found by the axe tests
- updated git actions to run the axe tests
### Why was this change made?
- To ensure that future changes don't break accessibility

## 29-09-2023
### What's new
- decrease wales obscure opacity
### Why was this change made?
- Some data we have is on wales, so we need to obscure it less

## 26-09-2023
### What's new
- Updated the base-tile set style changing min and max zoom levels for layers
### Why was this change made?
- To avoid the map being to cluttered and to make it easier to see the data

## 22-09-2023
### What's new
- Updated the title for the map to 'Map of planning data for England'
### Why was this change made?
- To make it clear that the map is only for England

## 22-09-2023
### What's new
- Moved the guidance for publishers link from the footer to the top nav
### Why was this change made?
- To make it easier for publishers to find the guidance

## 22-09-2023
- Added tinted layer over Wales and Scotland on map to indicate that the data isn't about them
- Added layer of europe
### Why was this change made?
- To make it clear that the data isn't about Wales and Scotland
- So the map doesn't look empty

## 15-09-2023
### What's new
- Updated layer controls css so it correctly displays on smaller screens
- overwrite scroll event for map popups/controls to prevent page scrolling
### Why was this change made?
- The layer controls would disappear on smaller screens
- The scroll event listener would cause the page to scroll when zooming on a map popup/control


## 15-09-2023
### What's new
- Updated circle radius on the map to interpolate between 8 and 0.8 based on zoom level
- Feature layers on the map now have a cursor pointer when hovered over
- OS copyright updated to specify Basemap contains OS data &copy; Crown copyright and database rights
- Zoom and centre now gets added to the url for the map, and when navigating back to the map page the map will be zoomed and centred to the previous location
### Why was this change made?
- Smaller circles on the map are easier to see
- The cursor pointer makes it more obvious that the feature is clickable
- To avoid people thinking that our data is owned by OS
- To make it easier to share a specific location on the map
***
<br />

## 13-09-2023
### What's new
- Back button now simulates window history back
- the back link now doesn't collide with the header on smaller screens
- the back button now correctly maintains the previous page state on the edge browser
### Why was this change made?
- Samantha requested that the back button should simulate the window history back
***
<br />

## 13-09-2023
### What's new
- The layer controls on the national map has been recoded to be a maplibre component
### Why was this change made?
- The previous layer controls wouldn't correctly appear in when the map was full screened
- this resolves tech debt surrounding this component
***
<br />

## 11-09-2023
### What's new
- fix the location search bar on the search page
***
<br />

## 07-09-2023
### What's new
- map popups now dont have a scroll event listener
### Why was this change made?
- previously, the scroll event listener would cause the page to scroll when zooming on the popup
***
<br />

## 07-09-2023
### What's new
- phase banner now has appropriate margin on the map page.
### Why was this change made?
- previously the phase banner looked out of place on the map page
***
<br />

## 07-09-2023
### What's new
- Search page: filters should be setup to show current entities by default
- Now only show typologies on the search page that have entities
### Why was this change made?
- showing historical entities from the start is confusing
- unnecessary to show typologies that have no entities
***
<br />

## 06-09-2023
### What's new
- hide cookie banner if js is disabled
### Why was this change made?
- we can't store cookies without js, so no need to show this
***
<br />

## 06-09-2023
### What's new
- update the map to use the base tile set from os maps
- setup oauth2 for use of the os maps
- changed the polygon layers to be of type fill-extrusion
### Why was this change made?
- maptiler would eventually revoke our key again, os maps is free for us to use
- we want to try and keep our os map key and secret secure so oauth2 helps us protect this
- 3D polygons look better than 2D polygons
***
<br />


## 04-09-2023
### What's new
- Fix the search bar on the datasets filters
### Why was this change made?
- To make the search bar work as intended
***
<br />

## 31-08-2023
### What's new
- Update docs pages to use more syntactical html
- Added descriptions to the api endpoints
- update about page to use more syntactical html
### Why was this change made?
- To make the page more accessible
***
<br />

## 30-08-2023
### What's new
- Update the home page to use more syntactical html
- Update the service status page to remove separators from the accessibility dom
### Why was this change made?
- To make the pages more accessible
***
<br />

## 25-08-2023
### What's new
- Make banner research sign up link open in a new tab
### Why was this change made?
- Request made by MJ
***
<br />

## 25-08-2023
### What's new
- Replaced breadcrumbs with a back button for all pages
### Why was this change made?
- The pages don't always follow a linier structure stable for breadcrumbs
- A back button is more consistent with the site design
***
<br />

## 25-08-2023
### What's new
- Added a new map component to be used across the whole site
### Why was this change made?
- Enables better map configuration and easier reuse
- Resolves some tech debt
***
<br />

## 24-08-2023
### What's new
- Move nav bar bellow page title on map page
### Why was this change made?
- To maintain consistency across the site
***
<br />

## 24-08-2023
### What's new
- Updated phase banner colour and text
### Why was this change made?
- To better make the banner stand out
- Also to link users to sign up for user research
***
<br />

## 24-08-2023
### What's new
- Updated Google Analytics javascript code to now get measurment ID from ENV
### Why was this change made?
- To remove the need to hard code the measurment ID in the javascript code
- To enable the use of Google Analytics in the development environment
***
<br />

## 16-08-2023
### What's new
- changed the base tile set and maptiler access key to George Goodall's personal key
### Why was this change made?
- Paul Smith's key was revoked
***

## 02-08-2023
### What's new
- changed guidance string to a header on the article-4-direction specification
***
<br />

## 12-07-2023
### What's new
- Added a change log mark down file
- Added a template for the change log
### Why was this change made?
- To keep track of changes made to the project
***
