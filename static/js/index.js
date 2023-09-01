// Initialize google map.
let map;

// async function return map based on address search form response coordinates.
async function initMap(coordinates) {
    // Coordinates of address form input
    const position = coordinates;
    // Request needed libraries.
    //@ts-ignore
    const { Map } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement } = await google.maps.importLibrary("marker");

    // The map, centered at position
    map = new Map(document.getElementById("map"), {
        zoom: 12,
        center: position,
        mapId: "8e0d75328319566e",
    });

    // The marker, positioned at coordinates
    const marker = new AdvancedMarkerElement({
        map: map,
        position: position,
        title: "Your search location",
    });
}

// Process address search form.
async function processForm(evt) {
    evt.preventDefault();

    let streetAddress = $("#address").val();
    let zipcode = $("#zipcode").val();
    let city = $("#city").val();
    let state = $("#state").val();
    let bedrooms = $("#bedrooms").val();

    let payload = {
        address: streetAddress,
        zipcode: zipcode,
        city: city,
        state: state,
    };

    let rentalPayload = {
        zipcode: zipcode,
    };

    let dbPayload = {
        address: streetAddress,
        zipcode: zipcode,
        city: city,
        state: state,
        bedrooms: bedrooms,
    };

    // save location data to DB
    const saveLocation = await axios.post("/adddata", dbPayload, {
        headers: { "Content-Type": "application/json" },
    });

    // retrieve address coordinates coordinates from '/api/geocode' python endpoint.
    const data = await axios
        .post("/api/geocode", payload, {
            headers: { "Content-Type": "application/json" },
        })
        .then(function (response) {
            console.log(response);
            return response;
        });

    const coordinates = data.data;
    console.log(coordinates);

    // retrieve rental averages from '/api/rental-data' python endpoint and display results
    const realtyData = await axios
        .post("/api/rental-data", rentalPayload, {
            headers: { "Content-Type": "application/json" },
        })
        .then(function (response) {
            console.log(response.data);
            if (response.data == "error") {
                window.location.replace("/search");
            }
            return response;
        });

    // check if data exists for search parameters.
    if (!realtyData["data"]["rentalData"]["detailed"][`${bedrooms}`]) {
        return $("#rental-data").html(
            `<br>
            <br>
            <div class="alert alert-warning" role="alert">No data available for ${bedrooms}-bedroom rentals in ${zipcode}.</div>`
        );
    } else {
        const average =
            realtyData["data"]["rentalData"]["detailed"][`${bedrooms}`][
                "averageRent"
            ];

        // Display results
        $("#rental-data").html(`
        <div class="container-fluid">
    <p class="h2">Rental Averages for ${zipcode}</p>
    <button id="favorite" type="submit" class="btn btn-outline-info" action="/favorites/add"> Save to favorites </button>
  <table class="table table-striped">
  <thead>
  <tr>
  <th scope="col">Bedrooms</th>
      <th scope="col">Average Rent in USD</th>
      </tr>
  </thead>
  <tbody>
    <tr>
      <th scope="row">${bedrooms}</th>
      <td>${average}</td>
    </tr>
    </tbody>
    </table>
    </div>
    `);
    }

    // add EventListener to save a search to favorites table in DB
    document.getElementById("favorite").addEventListener("click", saveFavorite);

    // Display Google Map with geocoordinates
    initMap(coordinates);
}

// on submit, process form.
$("#address-lookup-form").on("submit", processForm);

// FAVORITES
// ********************************************************
async function saveFavorite(evt) {
    // Save location to favorites table.
    evt.preventDefault();

    let zipcode = $("#zipcode").val();
    let address = $("#address").val();
    let bedrooms = $("#bedrooms").val();

    let rentalPayload = {
        zipcode: zipcode,
    };

    const realtyData = await axios
        .post("/api/rental-data", rentalPayload, {
            headers: { "Content-Type": "application/json" },
        })
        .then(function (response) {
            console.log(response);
            return response;
        });

    const average =
        realtyData["data"]["rentalData"]["detailed"][`${bedrooms}`][
            "averageRent"
        ];

    let favPayload = {
        average: average,
        zipcode: zipcode,
        address: address,
    };

    // Add location to favorites table via python endpoint.
    const addFavorite = await axios.post("/favorites/add", favPayload, {
        headers: { "Content-Type": "application/json" },
    });
}

// #############################################################
// Initialize favorites map.
let favsMap;

async function initFavsMap(coordinates) {
    // Display map with markers for each favorite in DB.

    // Request needed libraries.
    const { Map, InfoWindow } = await google.maps.importLibrary("maps");
    const { AdvancedMarkerElement, PinElement } =
        await google.maps.importLibrary("marker");
    const map = new Map(document.getElementById("map"), {
        zoom: 8,
        center: coordinates[0].position,
        mapId: "4504f8b37365c3d0",
    });

    const favorites = coordinates;
    // for (favorite in favorites) {
    //     console.log(favorite);
    // }

    // Create an info window to share between markers.
    const infoWindow = new InfoWindow();

    // Create the markers for each favorite.
    favorites.forEach(({ position, title }, i) => {
        const pin = new PinElement({
            glyph: `${i + 1}`,
        });
        const marker = new AdvancedMarkerElement({
            position,
            map,
            title: `${i + 1}. ${title}`,
            content: pin.element,
        });

        // Add a click listener for each marker, and set up the info window.
        marker.addListener("click", ({ domEvent, latLng }) => {
            const { target } = domEvent;

            infoWindow.close();
            infoWindow.setContent(marker.title);
            infoWindow.open(marker.map, marker);
        });
    });
}

async function loadFavorites() {
    // Get list of all favorites coordinates, loop through list to...
    // Display a marker for each favorite on map.
    // Display custom markers with rental & bedroom data for each favorite.

    // Get coordinates for each favorite from python endpoint.
    const data = await axios.get("/api/batchgeocode");
    console.log(data.data);

    // Get addresses for each favorite from python endpoint.
    const addresses = await axios.get("favorites/data");
    let favorites = addresses.data;
    console.log(favorites.length);

    let coordinates = data.data;
    let length = Object.keys(coordinates);

    // Create array of dict. objects to input into initFavsMap().
    let savedFaves = [];
    for (let i = 0; i < length.length; i++) {
        let position = {};
        console.log(coordinates[i]);
        position["position"] = coordinates[i];
        position["title"] = favorites[i];
        savedFaves.push(position);
    }

    // Display map of favorites.
    initFavsMap(savedFaves);
}

$("#display-map").on("click", loadFavorites);
