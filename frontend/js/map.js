
"use strict";

document.addEventListener("DOMContentLoaded", () => {
    const API_URL = "http://127.0.0.1:8000/api/map/locations/";
    const RADIUS_METRES = 30000;
    const EARTH_RADIUS_KM = 6371;

    const mapElement = document.getElementById("map");
    const statusElement = document.getElementById("map-status");
    const nearbyStatusElement = document.getElementById("nearby-status");
    const countElement = document.getElementById("location-count");
    const resetButton = document.getElementById("reset-map");
    const nearMeButton = document.getElementById("near-me");
    const filterButtons = document.querySelectorAll("[data-filter]");

    if (
        !mapElement ||
        !statusElement ||
        !countElement ||
        !resetButton ||
        !nearMeButton
    ) {
        console.error("Map page is missing one or more required HTML elements.");
        return;
    }

    if (typeof L === "undefined") {
        showStatus(
            "The map library could not load. Check your internet connection and refresh.",
            "error"
        );
        return;
    }

    const DEFAULT_CENTER = [-26.2041, 28.0473];
    const DEFAULT_ZOOM = 6;

    const map = L.map("map", {
        scrollWheelZoom: true
    }).setView(DEFAULT_CENTER, DEFAULT_ZOOM);

    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
        maxZoom: 19,
        attribution:
            '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank" rel="noopener noreferrer">OpenStreetMap</a> contributors'
    }).addTo(map);

    const markerLayers = {
        destination: L.layerGroup().addTo(map),
        event: L.layerGroup().addTo(map)
    };

    let allLocations = [];
    let visibleLocations = [];
    let activeFilter = "all";
    let userLocation = null;
    let nearbyMode = false;
    let userMarker = null;
    let radiusCircle = null;

    function showStatus(message, type = "") {
        statusElement.textContent = message;
        statusElement.className = "map-status";

        if (type) {
            statusElement.classList.add(type);
        }
    }

    function showNearbyStatus(message, type = "") {
        if (!nearbyStatusElement) {
            return;
        }

        nearbyStatusElement.textContent = message;
        nearbyStatusElement.className = "map-status";

        if (type) {
            nearbyStatusElement.classList.add(type);
        }
    }

    function escapeHTML(value) {
        return String(value ?? "").replace(/[&<>"']/g, (character) => {
            const entities = {
                "&": "&amp;",
                "<": "&lt;",
                ">": "&gt;",
                '"': "&quot;",
                "'": "&#39;"
            };

            return entities[character];
        });
    }

    function formatPrice(price) {
        if (price === null || price === undefined || price === "") {
            return "Price unavailable";
        }

        const amount = Number(price);

        if (!Number.isFinite(amount)) {
            return "Price unavailable";
        }

        if (amount === 0) {
            return "Free";
        }

        return new Intl.NumberFormat("en-ZA", {
            style: "currency",
            currency: "ZAR"
        }).format(amount);
    }

    function isValidLocation(location) {
        if (!location || typeof location !== "object") {
            return false;
        }

        const latitude = Number(location.latitude);
        const longitude = Number(location.longitude);

        return (
            (location.type === "destination" || location.type === "event") &&
            typeof location.name === "string" &&
            location.name.trim().length > 0 &&
            location.latitude !== null &&
            location.latitude !== undefined &&
            location.longitude !== null &&
            location.longitude !== undefined &&
            Number.isFinite(latitude) &&
            Number.isFinite(longitude) &&
            latitude >= -90 &&
            latitude <= 90 &&
            longitude >= -180 &&
            longitude <= 180
        );
    }

    // Haversine formula: calculate straight-line distance between two coordinates.
    function distanceInKm(start, end) {
        const toRadians = (degrees) => degrees * Math.PI / 180;

        const latitudeDifference = toRadians(end[0] - start[0]);
        const longitudeDifference = toRadians(end[1] - start[1]);

        const startLatitude = toRadians(start[0]);
        const endLatitude = toRadians(end[0]);

        const a =
            Math.sin(latitudeDifference / 2) ** 2 +
            Math.cos(startLatitude) *
            Math.cos(endLatitude) *
            Math.sin(longitudeDifference / 2) ** 2;

        const boundedA = Math.min(1, Math.max(0, a));

        return 2 * EARTH_RADIUS_KM *
            Math.atan2(Math.sqrt(boundedA), Math.sqrt(1 - boundedA));
    }

    function createPopup(location) {
        const typeLabel =
            location.type === "event" ? "Event" : "Destination";

        const typeClass = location.type === "event" ? "event" : "";

        const description = location.description
            ? `<p class="popup-description">${escapeHTML(location.description)}</p>`
            : "";

        const city = location.city
            ? `<p class="popup-meta">${escapeHTML(location.city)}</p>`
            : "";

        const distance = nearbyMode && userLocation
            ? `<p class="popup-meta"><strong>${distanceInKm(
                userLocation,
                [Number(location.latitude), Number(location.longitude)]
            ).toFixed(1)} km away</strong></p>`
            : "";

        return `
            <div class="map-popup">
                <p class="popup-type ${typeClass}">${typeLabel}</p>
                <h3 class="popup-title">${escapeHTML(location.name)}</h3>
                ${description}
                ${city}
                ${distance}
                <p class="popup-meta">${escapeHTML(formatPrice(location.price))}</p>
            </div>
        `;
    }

    function createMarker(location) {
        const coordinates = [
            Number(location.latitude),
            Number(location.longitude)
        ];

        const color = location.type === "event" ? "#d97736" : "#2b8258";

        const markerIcon = L.divIcon({
            className: "custom-map-marker",
            html: `
                <span style="
                    display: block;
                    width: 18px;
                    height: 18px;
                    background: ${color};
                    border: 3px solid white;
                    border-radius: 50%;
                    box-shadow: 0 2px 7px rgba(0,0,0,0.35);
                "></span>
            `,
            iconSize: [18, 18],
            iconAnchor: [9, 9],
            popupAnchor: [0, -10]
        });

        return L.marker(coordinates, {
            icon: markerIcon,
            title: location.name,
            alt: `${location.name}, ${location.type}`
        }).bindPopup(createPopup(location));
    }

    function updateCount() {
        countElement.textContent = String(visibleLocations.length);
    }

    function getFilteredLocations() {
        let locations = allLocations.filter((location) => {
            return activeFilter === "all" || location.type === activeFilter;
        });

        if (nearbyMode && userLocation) {
            locations = locations.filter((location) => {
                const coordinates = [
                    Number(location.latitude),
                    Number(location.longitude)
                ];

                return distanceInKm(userLocation, coordinates) <=
                    RADIUS_METRES / 1000;
            });

            locations.sort((first, second) => {
                const firstDistance = distanceInKm(userLocation, [
                    Number(first.latitude),
                    Number(first.longitude)
                ]);

                const secondDistance = distanceInKm(userLocation, [
                    Number(second.latitude),
                    Number(second.longitude)
                ]);

                return firstDistance - secondDistance;
            });
        }

        return locations;
    }

    function renderMarkers() {
        markerLayers.destination.clearLayers();
        markerLayers.event.clearLayers();

        visibleLocations = getFilteredLocations();

        visibleLocations.forEach((location) => {
            markerLayers[location.type].addLayer(createMarker(location));
        });

        updateCount();

        if (nearbyMode && userLocation) {
            showNearbyStatus(
                `Showing ${visibleLocations.length} ${
                    visibleLocations.length === 1 ? "place" : "places"
                } within 30 km of your location.`,
                "success"
            );
        }

        if (visibleLocations.length === 0) {
            showStatus(
                nearbyMode
                    ? "No destinations or events within 30 km match this filter. Try another filter or reset the map."
                    : allLocations.length === 0
                        ? "No mapped locations are available yet. Add coordinates to destinations or events to display them here."
                        : `No ${activeFilter === "all" ? "locations" : activeFilter + "s"} found. Try another filter.`,
                "success"
            );
            return;
        }

        showStatus(
            `Showing ${visibleLocations.length} ${
                visibleLocations.length === 1 ? "location" : "locations"
            }${nearbyMode ? " nearby" : ""}.`,
            "success"
        );

        if (nearbyMode && userLocation) {
            // Keep the user location and radius visible even when there are no nearby markers.
            map.fitBounds(radiusCircle.getBounds(), {
                padding: [25, 25]
            });
            return;
        }

        const coordinates = visibleLocations.map((location) => [
            Number(location.latitude),
            Number(location.longitude)
        ]);

        if (coordinates.length === 1) {
            map.setView(coordinates[0], 12);
        } else {
            map.fitBounds(L.latLngBounds(coordinates), {
                padding: [35, 35],
                maxZoom: 12
            });

            if (map.getZoom() < 6) {
                map.setView(DEFAULT_CENTER, DEFAULT_ZOOM);
            }
        }
    }

    function updateActiveFilter(selectedButton) {
        filterButtons.forEach((button) => {
            const isActive = button === selectedButton;

            button.classList.toggle("active", isActive);
            button.setAttribute("aria-pressed", String(isActive));
        });
    }

    function enableNearbyMode(coordinates) {
        userLocation = coordinates;
        nearbyMode = true;

        if (userMarker) {
            map.removeLayer(userMarker);
        }

        if (radiusCircle) {
            map.removeLayer(radiusCircle);
        }

        userMarker = L.circleMarker(userLocation, {
            radius: 8,
            color: "#ffffff",
            weight: 3,
            fillColor: "#2563eb",
            fillOpacity: 1
        }).addTo(map).bindPopup("Your location");

        radiusCircle = L.circle(userLocation, {
            radius: RADIUS_METRES,
            color: "#2563eb",
            weight: 2,
            fillColor: "#60a5fa",
            fillOpacity: 0.12
        }).addTo(map);

        nearMeButton.textContent = "Refresh my location";
        renderMarkers();
    }

    function requestUserLocation() {
        if (!navigator.geolocation) {
            showNearbyStatus(
                "Your browser does not support location services. You can still explore the map normally.",
                "error"
            );
            return;
        }

        nearMeButton.disabled = true;
        showNearbyStatus("Requesting your location...");

        navigator.geolocation.getCurrentPosition(
            (position) => {
                nearMeButton.disabled = false;

                enableNearbyMode([
                    position.coords.latitude,
                    position.coords.longitude
                ]);
            },
            (error) => {
                nearMeButton.disabled = false;

                let message =
                    "We couldn't access your location. You can still explore the full map.";

                if (error.code === error.PERMISSION_DENIED) {
                    message =
                        "Location permission was denied. Allow location access in your browser settings, then try again.";
                } else if (error.code === error.POSITION_UNAVAILABLE) {
                    message =
                        "Your location is currently unavailable. Check your device location settings and try again.";
                } else if (error.code === error.TIMEOUT) {
                    message =
                        "Location request timed out. Please try again.";
                }

                showNearbyStatus(message, "error");
            },
            {
                enableHighAccuracy: true,
                timeout: 12000,
                maximumAge: 60000
            }
        );
    }

    function resetMap() {
        nearbyMode = false;
        userLocation = null;

        if (userMarker) {
            map.removeLayer(userMarker);
            userMarker = null;
        }

        if (radiusCircle) {
            map.removeLayer(radiusCircle);
            radiusCircle = null;
        }

        nearMeButton.textContent = "Find near me";
        showNearbyStatus(
            'Select "Find near me" to discover places within 30 km.'
        );

        renderMarkers();
    }

    async function loadLocations() {
        showStatus("Loading destinations and events...");

        try {
            const response = await fetch(API_URL, {
                method: "GET",
                headers: {
                    Accept: "application/json"
                }
            });

            if (!response.ok) {
                throw new Error(`API request failed with status ${response.status}`);
            }

            const data = await response.json();

            if (!Array.isArray(data)) {
                throw new Error("The map API returned an unexpected response.");
            }

            allLocations = data.filter(isValidLocation);

            if (allLocations.length !== data.length) {
                console.warn(
                    `${data.length - allLocations.length} invalid map records were ignored.`
                );
            }

            renderMarkers();
        } catch (error) {
            console.error("Unable to load map locations:", error);
            allLocations = [];
            visibleLocations = [];
            markerLayers.destination.clearLayers();
            markerLayers.event.clearLayers();
            updateCount();

            showStatus(
                "We couldn't load locations. Check that the Django server is running and the map API is reachable, then refresh.",
                "error"
            );
        }
    }

    filterButtons.forEach((button) => {
        button.addEventListener("click", () => {
            activeFilter = button.dataset.filter;
            updateActiveFilter(button);
            renderMarkers();
        });
    });

    nearMeButton.addEventListener("click", requestUserLocation);
    resetButton.addEventListener("click", resetMap);

    loadLocations();
});
