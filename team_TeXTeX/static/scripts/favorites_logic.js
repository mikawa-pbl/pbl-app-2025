document.addEventListener('DOMContentLoaded', function () {
  // CSRF Token Helper
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      const cookies = document.cookie.split(';');
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }
  const csrftoken = getCookie('csrftoken');

  // Event Delegation for Star Icons
  document.body.addEventListener('click', function (e) {
    if (e.target.classList.contains('star-icon')) {
      console.log('Star icon clicked');
      const star = e.target;
      const slug = star.dataset.slug;
      if (slug) {
        toggleFavorite(slug, star);
      } else {
        console.error("No slug found on star icon");
      }
    }
  });

  function toggleFavorite(slug, starElement) {
    const url = window.favoriteToggleUrl || '/team_TeXTeX/api/favorite_toggle/'; // フォールバック
    console.log(`Toggling favorite: ${slug} at ${url}`);

    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrftoken
      },
      body: JSON.stringify({ slug: slug })
    })
      .then(response => response.json())
      .then(data => {
        if (data.status === 'added' || data.status === 'removed') {
          updateUI(data.status, slug);
        } else if (data.error) {
          console.error('Error:', data.error);
        }
      })
      .catch(error => console.error('Error:', error));
  }

  function updateUI(status, slug) {
    // Find all stars with this slug
    const stars = document.querySelectorAll(`.star-icon[data-slug="${slug}"]`);

    if (status === 'added') {
      // Activate all stars
      stars.forEach(s => s.classList.add('active'));
      addToFavoritesTab(slug);
    } else {
      // Deactivate all stars
      stars.forEach(s => s.classList.remove('active'));
      removeFromFavoritesTab(slug);
    }
  }

  function addToFavoritesTab(slug) {
    const favoritesList = document.getElementById('favorites-list');
    if (!favoritesList) return;

    // Check if already in favorites list
    if (favoritesList.querySelector(`li > .star-icon[data-slug="${slug}"]`)) return;

    // Find the original item to clone
    const originalStar = document.querySelector(`details:not(#favorites-group) .star-icon[data-slug="${slug}"]`);
    if (originalStar) {
      const originalLi = originalStar.closest('li');
      if (originalLi) {
        const newLi = originalLi.cloneNode(true);
        // Ensure the star is active
        newLi.querySelector('.star-icon').classList.add('active');
        favoritesList.appendChild(newLi);
      }
    }
  }

  function removeFromFavoritesTab(slug) {
    const favoritesList = document.getElementById('favorites-list');
    if (!favoritesList) return;

    const itemToRemove = favoritesList.querySelector(`li > .star-icon[data-slug="${slug}"]`);
    if (itemToRemove) {
      const li = itemToRemove.closest('li');
      li.remove();
    }
  }
});
