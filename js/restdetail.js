document.addEventListener("DOMContentLoaded", () => {
  const heartButton = document.querySelector(".heart-btn");

  heartButton.addEventListener("click", () => {
    const restaurantData = {
      name: "{{ rest[1] }}",
      description: "{{ rest[10] }}",
      cuisine: "{{ rest[4] }}",
      id: "{{ rest[0] }}" // Assuming restaurant's ID is available
    };

    fetch("/api/wishlist/add", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(restaurantData)
    })
    .then(response => {
      if (response.status === 401) {
        // If not logged in, redirect to login
        window.location.href = "/login";
      } else if (response.ok) {
        // If successful, fill the heart icon
        heartButton.innerHTML = "&#10084;"; // Filled heart symbol
      } else {
        alert("Error adding to wishlist. Please try again.");
      }
    })
    .catch(error => {
      console.error("Error:", error);
      alert("An error occurred. Please try again.");
    });
  });
});
