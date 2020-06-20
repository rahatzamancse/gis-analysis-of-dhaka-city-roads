const mymap = L.map("map").setView([23.8103, 90.4125], 13);

L.tileLayer(
  "https://api.tiles.mapbox.com/v4/{id}/{z}/{x}/{y}.png?access_token={accessToken}",
  {
    attribution:
      'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, <a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, Imagery © <a href="https://www.mapbox.com/">Mapbox</a>',
    maxZoom: 18,
    id: "mapbox.streets",
    accessToken:
      "pk.eyJ1IjoicmFpaGFudWwtcmVmYXQiLCJhIjoiY2syYzYyb3ppMjVrajNibzBiajdzbHgwcCJ9.JmKhZFXQYLBRG8BwFBjx9Q"
  }
).addTo(mymap);

function showKMLOnMap(kml) {
  const track = new L.KML(kml);
  mymap.addLayer(track);

  // Adjust map to show the kml
  const bounds = track.getBounds();
  mymap.fitBounds(bounds);
}

function query() {
  return fetch("assets/ex1.kml")
    .then(res => res.text())
    .then(kmltext => {
      // Create new kml overlay
      const parser = new DOMParser();
      const kml = parser.parseFromString(kmltext, "text/xml");

      showKMLOnMap(kml);
    });
}

let src = new L.Marker([23.734, 90.3928], {
  draggable: true,
  autoPan: true,
  title: "Source"
}).addTo(mymap);
let dst = new L.Marker([23.738, 90.393], {
  draggable: true,
  autoPan: true,
  title: "Destination"
}).addTo(mymap);

$("#center-map").click(e => {
  mymap.panTo([23.734, 90.3928]);
});

$("#get-dir").click(e => {
  let srcLatLng = src.getLatLng();
  let dstLatLng = dst.getLatLng();
  let info = "src: " + srcLatLng + " dst: " + dstLatLng;
  $("p#status-text").text("Status: Processing with " + info);
  setTimeout(() => {
    query()
      .then(() => {
        $("p#status-text").text("Status: Done with " + info);
      })
      .catch(() => {
        $("p#status-text").text(
          "Status: Error with fetch API... CORS... need real webserver like Django etc"
        );
      });
  }, 2000);
});
