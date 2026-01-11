
function registerCategoryEvents(){
    const categories = document.getElementsByClassName('category-link');
    Array.from(categories).forEach(element => {
        element.addEventListener('click', function(event) {
            const categoryId = event.target.dataset.id
            if (event.target.tagName === 'A' && categoryId) {
                event.preventDefault();

                const parentNode = event.target.parentNode;
                const categorySlug = event.target.dataset.slug;
                const currentUrl = window.location.href;
                const paramStart = currentUrl.indexOf('?') >= 0 ? currentUrl.indexOf('?') : currentUrl.indexOf('blog') + 4
                const paramString = currentUrl.substring(paramStart, currentUrl.length );

                let params = new URLSearchParams(paramString);
                if( parentNode.classList.contains('active') ) {
                    params.delete('category', categorySlug);
                } else {
                    const updated_cats = params.get('category') ? params.get('category') + ',' + categorySlug : categorySlug;
                    params.set('category', updated_cats);
                }

                params.set('page', 1);
                fetchPosts("blog?" + params.toString());

                parentNode.classList.contains('active') ? parentNode.classList.remove("active") : parentNode.classList.add("active");
            }
        });
    });
}

function registerPaginationEvents() {
  const paginationContainer = document.getElementById('pagination-container');

  if (paginationContainer) {
      paginationContainer.addEventListener('click', function(event) {
          if (event.target.tagName === 'A' && event.target.dataset.page) {
              event.preventDefault();
              const page = event.target.dataset.page;

               const categorySlug = event.target.dataset.slug;
                const currentUrl = window.location.href;
                const paramStart = currentUrl.indexOf('?') >= 0 ? currentUrl.indexOf('?') : currentUrl.indexOf('blog') + 4
                const paramString = currentUrl.substring(paramStart, currentUrl.length );

                let params = new URLSearchParams(paramString);
                params.set('page', page);
                fetchPosts("blog?" + params.toString());
          }
      });
  }
}

function registerSearchEvents() {
    const searchForm = document.getElementById('search-form');
    const searchInput = document.getElementById('search-input');

    if (searchForm) {
      searchForm.addEventListener('submit', function(event) {
        event.preventDefault();

        const searchTerm = searchInput.value;
        const currentUrl = window.location.href;
        const paramStart = currentUrl.indexOf('?') >= 0 ? currentUrl.indexOf('?') : currentUrl.indexOf('blog') + 4
        const paramString = currentUrl.substring(paramStart, currentUrl.length );

        let params = new URLSearchParams(paramString);
        params.set('s', searchTerm);
        params.set('page', 1);
        fetchPosts("blog?" + params.toString());
      });
    }
}

function registerClearEvents(){
    const clearButton = document.getElementById('clear');
    const searchInput = document.getElementById('search-input');
    const categories = document.getElementsByClassName('category');

    if ( clearButton ) {
        clearButton.addEventListener('click', function(){
             Array.from(categories).forEach(category => {
                category.classList.remove("active");
            });
            searchInput.value = '';
            fetchPosts("blog?");
        });
    }
}

function fetchPosts(page) {
//    const url = new URL(window.location.href);
    const apiUrl = page
    fetch(apiUrl, {
      headers: {
          'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        updateResultContent(data);
        updatePaginationUI(data);
        window.history.pushState("", "", apiUrl);
    })
    .catch(error => console.error('Error fetching posts:', error));
}

function updateResultContent(data) {
    const blogContainer = document.getElementById('blogs-container');
    if( blogContainer ) {
        blogContainer.innerHTML = '';

        if ( data.posts.length <= 0 ) {
            const noResults = document.createElement('h2');
            noResults.innerHTML = 'No results found';
            blogContainer.appendChild(noResults);
            return;
        }

        data.posts.forEach(post => {
            const cardContent = `<a href="/blog/${post.title.replaceAll(' ', '-')}"><div class="media image featured"><img class="card-img" src="${post.image_url}" alt="" style="aspect-ratio: 2/1; object-fit: cover; "></div><div class="text"><h2>${post.title}</h2>${post.content}</div></a>`;
            const card = document.createElement('div');
            card.classList.add('card');
            card.innerHTML = cardContent;
            blogContainer.appendChild(card);
        });
    }
}

function updatePaginationUI(data) {
    const pagination = document.getElementById('pagination-container');
    // If we dont have enough items to display on more than one page, hide pagination entirely.
    if ( data.posts.length <= 1 && data.current_page == 1 || data.total_pages == 1 ) {
        pagination.style.display = 'none';
    } else {
        pagination.style.display = 'block';

        const page_links = document.getElementsByClassName('page-link');
        Array.from(page_links).forEach(link => {
            if ( link.dataset.page == data.current_page ) {
                link.classList.add("active");
            } else {
                link.classList.remove("active");
            }

            if( link.dataset.page > data.total_pages ) {
                link.style.display = 'none';
            } else {
                link.style.display = 'inline-block';
            }
        });
    }
}

function toggleMenu() {
    const hamburgerDots = document.getElementById('dots');
    const primaryMenu = document.getElementById('header-nav');

    hamburgerDots.addEventListener('click', function(event) {
        hamburgerDots.classList.contains('on') ? hamburgerDots.classList.remove("on") : hamburgerDots.classList.add("on");

        if ( primaryMenu.classList.contains('open') ) {
            primaryMenu.classList.remove("open");
            setTimeout(function(){
                primaryMenu.classList.add("hidden");
            }, 1000);

        } else {
            primaryMenu.classList.add("open");
            primaryMenu.classList.remove("hidden");

        }
    });
}

function toggleFilters() {
    const filterButton = document.getElementById('filter-button');
    const blogFilterContent = document.getElementById('filter-content');
    const filterClose = document.getElementById('filter-close');

    if ( filterButton ) {
        filterButton.addEventListener('click', function(event) {
            blogFilterContent.classList.contains('open') ? blogFilterContent.classList.remove("open") : blogFilterContent.classList.add("open");
        });
    }

    if ( filterClose ) {
        filterClose.addEventListener('click', function(event) {
            blogFilterContent.classList.remove("open");
        });
    }
}

function toggleWorkSample() {
    const workSamples = document.getElementsByClassName('work-samples__item');
    const overlay = document.getElementById('work-samples__overlay');
    const overlayClose = document.getElementById('blog-overlay-close');

    if ( workSamples && overlay ) {
        Array.from(workSamples).forEach(element => {
            const name = document.getElementById('overlay-name');
            const description = document.getElementById('overlay-description');
            const url = document.getElementById('overlay-url');
            const tooling = document.getElementById('overlay-tooling');
            const responsibilities = document.getElementById('overlay-responsibilities');

            element.addEventListener('click', function(event) {

                const apiUrl = window.location.origin + '/portfolio/entry/' + event.target.dataset.id;

                fetch(apiUrl, {
                  headers: {
                      'X-Requested-With': 'XMLHttpRequest'
                  }
                })
                .then(response => response.json())
                .then(data => {
                    name.innerHTML = data.name;
                    description.innerHTML = data.description;
                    tooling.innerHTML = data.tooling;
                    url.href = data.external_url;
                    responsibilities.innerHTML = data.responsibilities;

                })
                .catch(error => console.error('Error fetching posts:', error));

                overlay.classList.add("open");
            });
        });
    }

    if ( overlayClose && overlay ) {
         overlayClose.addEventListener('click', function(event) {
            overlay.classList.remove("open");
        });
    }
}

document.addEventListener('DOMContentLoaded', function() {
   registerPaginationEvents();
   registerCategoryEvents();
   registerSearchEvents();
   registerClearEvents();
   toggleMenu();
   toggleFilters();
   toggleWorkSample();
});