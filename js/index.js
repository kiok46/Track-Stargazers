var COLORS = [
    "#1abc9c" , "#2ecc71" , "#3498db"
  , "#9b59b6" , "#34495e" , "#16a085"
  , "#27ae60" , "#2980b9" , "#8e44ad"
  , "#2c3e50" , "#f1c40f" , "#e67e22"
  , "#e74c3c" , "#ecf0f1" , "#95a5a6"
  , "#f39c12" , "#d35400" , "#c0392b"
  , "#bdc3c7" , "#7f8c8d"
];

var fills = {
  defaultFill: '#3498db'
};

threeLeterCountryCodes.forEach(function (c, i) {
    fills[c] = COLORS[i % COLORS.length];
});

function createMap(id, data) {
    var map = new Datamap({
      element: document.getElementById(id),
      geographyConfig: {
        popupOnHover: false,
        highlightOnHover: false
      },
      fills: fills
    });
    map.bubbles(data, {
      popupTemplate: function(geo, data) {
        return '<div class="hoverinfo">Country: <strong>' + data.country + '</strong><br>Stargazers: <strong>' + data.stars  + '</strong></div>';
      }
    });
}

function formatDate(d) {
    var months = [
        'January','February','March',
        'April','May','June','July',
        'August','Sepember','October',
        'November','December'
    ];
    return [months[d.getMonth()], d.getDate(), d.getFullYear()].join(" ");
}

var countries = {};
var cNames = {};
var maxStargazers = -Infinity;
var maxUsers = -Infinity;
var allUniqueUsers = {};

document.getElementById("last-updated-at").innerHTML = formatDate(DATA.created_at);

DATA.users.forEach(c => {
    allUniqueUsers[c.user] = 1;
    c.countryCode = getCountryCode(c.country);
    cNames[c.countryCode] = c.country;
    var arr = countries[c.countryCode] = countries[c.countryCode] || []
    arr.push(c);
    if (arr.length > maxStargazers) {
        maxStargazers = arr.length;
    }
});

var maxRadius = 100;

var sessionsData = Object.keys(countries).map(c => {
    var country = countries[c];
    var stars = country.length;
    var r = maxRadius * stars / maxStargazers;

    return {
        radius: r > 60 ? 60 : r < 10 ? 10 : r
      , centered: c
      , stars: stars
      , country: cNames[country[0].countryCode]
      , fillKey: c
    };
});
document.getElementById("happy-people-count").innerHTML = Object.keys(allUniqueUsers).length.toString();

createMap("stargazers-map", sessionsData);