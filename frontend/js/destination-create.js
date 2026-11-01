(() => {
  "use strict";

  // Django API runs on port 8000; Live Server runs on port 5500.
  const API_BASE = "http://127.0.0.1:8000";
  const DESTINATIONS_URL = `${API_BASE}/api/destinations/`;
  const INTERESTS_URL = `${API_BASE}/api/interests/`;
  const GEOCODING_URL = "https://nominatim.openstreetmap.org/search";

  const form = document.getElementById("destination-form");
  const interestSelect = document.getElementById("interest");
  const searchInput = document.getElementById("address-query");
  const searchButton = document.getElementById("search-address");
  const resultsContainer = document.getElementById("address-results");
  const selectedContainer = document.getElementById("selected-address");
  const message = document.getElementById("message");
  const submitButton = document.getElementById("submit-destination");

  let selectedLocation = null;

  // Get the JWT access token saved during login.
  function getToken() {
    for (const key of ["access", "access_token", "token"]) {
      const token = localStorage.getItem(key);

      if (token && token !== "undefined" && token !== "null") {
        return token;
      }
    }

    return "";
  }

  // Build headers without sending an invalid Authorization header.
  function getHeaders(includeJson = false) {
    const headers = {};

    if (includeJson) {
      headers["Content-Type"] = "application/json";
    }

    const token = getToken();

    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

    return headers;
  }

  async function readResponse(response) {
    const text = await response.text();

    let data;

    try {
      data = text ? JSON.parse(text) : {};
    } catch {
      data = { detail: text || "The server returned an invalid response." };
    }

    if (!response.ok) {
      const detail =
        data.detail ||
        data.message ||
        JSON.stringify(data);

      throw new Error(`HTTP ${response.status}: ${detail}`);
    }

    return data;
  }

  function showMessage(text, isError = false) {
    message.textContent = text;
    message.style.color = isError ? "#b42318" : "#26834a";
  }

  // Support standard DRF arrays and paginated DRF responses.
  function getList(data) {
    if (Array.isArray(data)) return data;
    if (Array.isArray(data.results)) return data.results;
    if (Array.isArray(data.interests)) return data.interests;
    return [];
  }

  // Load interests into the dropdown.
  async function loadInterests() {
    interestSelect.replaceChildren(
      new Option("Loading interests...", "")
    );

    try {
      const response = await fetch(INTERESTS_URL, {
        method: "GET",
        headers: getHeaders()
      });

      const data = await readResponse(response);
      const interests = getList(data);

      interestSelect.replaceChildren(
        new Option("Select an interest", "")
      );

      interests.forEach((interest) => {
        const id = interest.id ?? interest.pk;
        const name =
          interest.name ??
          interest.title ??
          interest.interest;

        if (id == null || !name) return;

        interestSelect.add(
          new Option(name, String(id))
        );
      });

      if (interestSelect.options.length === 1) {
        interestSelect.replaceChildren(
          new Option("No interests available", "")
        );

        showMessage(
          "No interests were returned. Check the interests API.",
          true
        );
      }
    } catch (error) {
      console.error("Could not load interests:", error);

      interestSelect.replaceChildren(
        new Option("Failed to load interests", "")
      );

      showMessage(
        `Could not load interests. ${error.message}`,
        true
      );
    }
  }

  // Clear the selected address whenever the search changes.
  searchInput.addEventListener("input", () => {
    selectedLocation = null;
    selectedContainer.hidden = true;
    selectedContainer.textContent = "";
    resultsContainer.replaceChildren();
  });

  // Search for addresses in South Africa using OpenStreetMap Nominatim.
  async function searchAddresses() {
    const query = searchInput.value.trim();

    if (query.length < 3) {
      showMessage("Enter at least three characters to search.", true);
      return;
    }

    searchButton.disabled = true;
    resultsContainer.replaceChildren();
    showMessage("Searching for addresses...");

    try {
      const params = new URLSearchParams({
        q: query + ", South Africa",
        format: "jsonv2",
        countrycodes: "za",
        limit: "5",
        addressdetails: "1"
      });

      const response = await fetch(
        `${GEOCODING_URL}?${params.toString()}`,
        {
          headers: {
            Accept: "application/json"
          }
        }
      );

      const data = await readResponse(response);

      if (!Array.isArray(data) || data.length === 0) {
        showMessage(
          "No matching addresses found. Try a more specific address.",
          true
        );
        return;
      }

      data.forEach((place) => {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = place.display_name;

        button.addEventListener("click", () => {
          const latitude = Number(place.lat);
          const longitude = Number(place.lon);

          if (
            !Number.isFinite(latitude) ||
            !Number.isFinite(longitude) ||
            latitude < -90 ||
            latitude > 90 ||
            longitude < -180 ||
            longitude > 180
          ) {
            showMessage("The selected coordinates are invalid.", true);
            return;
          }

          selectedLocation = {
            address: place.display_name,
            latitude,
            longitude
          };

          selectedContainer.textContent =
            `Selected address: ${place.display_name}\n` +
            `Coordinates: ${latitude}, ${longitude}`;

          selectedContainer.hidden = false;
          resultsContainer.replaceChildren();

          showMessage("Address selected successfully.");
        });

        resultsContainer.appendChild(button);
      });

      showMessage("Select the correct address from the results.");
    } catch (error) {
      console.error("Address search failed:", error);

      showMessage(
        `Address search failed: ${error.message}`,
        true
      );
    } finally {
      searchButton.disabled = false;
    }
  }

  searchButton.addEventListener("click", searchAddresses);

  searchInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
      event.preventDefault();
      searchAddresses();
    }
  });

  // Submit the destination to Django.
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!getToken()) {
      showMessage(
        "You must log in first. No access token was found in localStorage.",
        true
      );
      return;
    }

    if (!selectedLocation) {
      showMessage(
        "Search for an address and select a result before saving.",
        true
      );
      searchInput.focus();
      return;
    }

    const name = document.getElementById("name").value.trim();
    const description =
      document.getElementById("description").value.trim();
    const price = Number(document.getElementById("price").value);
    const city =
      document.getElementById("city").value.trim() ||
      "Johannesburg";
    const interest = interestSelect.value;

    if (!name) {
      showMessage("Destination name is required.", true);
      return;
    }

    if (!interest) {
      showMessage("Please select an interest.", true);
      return;
    }

    if (!Number.isFinite(price) || price < 0) {
      showMessage("Enter a valid, non-negative price.", true);
      return;
    }

    // These field names must match your Django serializer.
    const destination = {
      name,
      description,
      price,
      city,
      interest: Number(interest),
      address: selectedLocation.address,
      latitude: selectedLocation.latitude,
      longitude: selectedLocation.longitude
    };

    submitButton.disabled = true;
    showMessage("Saving destination...");

    try {
      const response = await fetch(DESTINATIONS_URL, {
        method: "POST",
        headers: getHeaders(true),
        body: JSON.stringify(destination)
      });

      const data = await readResponse(response);

      showMessage(
        `Destination "${data.name || name}" saved successfully!`
      );

      form.reset();
      selectedLocation = null;
      selectedContainer.hidden = true;
      selectedContainer.textContent = "";
      resultsContainer.replaceChildren();

      document.getElementById("city").value = "Johannesburg";

      await loadInterests();
    } catch (error) {
      console.error("Destination creation failed:", error);

      showMessage(
        `Could not save destination: ${error.message}`,
        true
      );
    } finally {
      submitButton.disabled = false;
    }
  });

  // Start the form.
  loadInterests();
})();