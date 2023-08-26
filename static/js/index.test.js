describe("Init Map", function () {
    it("should initialize the map with provided coordinates", async function () {
        // Mock the google.maps.importLibrary function
        spyOn(google.maps, "importLibrary").and.returnValue(
            Promise.resolve({
                Map: function () {},
                AdvancedMarkerElement: function () {},
            })
        );

        const coordinates = { lat: 40.7128, lng: -74.006 };
        await initMap(coordinates);

        // Check if google.maps.importLibrary was called with correct parameters
        expect(google.maps.importLibrary).toHaveBeenCalledWith("maps");
        expect(google.maps.importLibrary).toHaveBeenCalledWith("marker");

        // Check if the map and marker were created with correct parameters
        expect(map).toBeDefined();
        expect(map instanceof google.maps.Map).toBe(true);
        expect(marker).toBeDefined();
        expect(marker instanceof google.maps.AdvancedMarkerElement).toBe(true);
    });
});

describe("Process Form", function () {
    it("should process the form and display rental data and map", async function () {
        // Mock the axios.post function
        spyOn(axios, "post").and.returnValues(
            Promise.resolve({ data: { lat: 40.7128, lng: -74.006 } }), // Mock geocode response
            Promise.resolve({
                data: {
                    rentalData: { detailed: { 3: { averageRent: 2000 } } },
                },
            }) // Mock rental data response
        );

        // Mock the document.getElementById function
        document.getElementById = jasmine.createSpy().and.returnValue({
            addEventListener: function () {},
        });

        // Mock the $ function (jQuery)
        window.$ = jasmine.createSpy().and.returnValue({
            val: function () {},
            html: function () {},
        });

        // Mock the initMap function
        spyOn(window, "initMap");

        // Mock the saveFavorite function
        spyOn(window, "saveFavorite");

        // Mock the window.location.replace function
        spyOn(window.location, "replace");

        // Simulate form submit
        await processForm({ preventDefault: function () {} });

        // Check if axios.post was called with correct parameters
        expect(axios.post).toHaveBeenCalledWith(
            "/api/geocode",
            jasmine.any(Object),
            {
                headers: { "Content-Type": "application/json" },
            }
        );
        expect(axios.post).toHaveBeenCalledWith(
            "/api/rental-data",
            jasmine.any(Object),
            {
                headers: { "Content-Type": "application/json" },
            }
        );

        // Check if initMap was called with correct coordinates
        expect(initMap).toHaveBeenCalledWith({ lat: 40.7128, lng: -74.006 });

        // Check if the rental data was displayed correctly
        expect(window.$().html).toHaveBeenCalledWith(
            jasmine.any(String) // Add your expected HTML here for the rental data
        );

        // Check if saveFavorite and addEventListener were called correctly
        expect(window.saveFavorite).toHaveBeenCalled();
        expect(document.getElementById).toHaveBeenCalledWith("favorite");
        expect(document.getElementById().addEventListener).toHaveBeenCalled();
    });
});

describe("Save Favorite", function () {
    it("should save the favorite to the database", async function () {
        // Mock the axios.post function
        spyOn(axios, "post").and.returnValue(Promise.resolve({}));

        // Simulate saveFavorite call
        await saveFavorite({ preventDefault: function () {} });

        // Check if axios.post was called with correct parameters
        expect(axios.post).toHaveBeenCalledWith(
            "/favorites/add",
            jasmine.any(Object),
            {
                headers: { "Content-Type": "application/json" },
            }
        );
    });
});
