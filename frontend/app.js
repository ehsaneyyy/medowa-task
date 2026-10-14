const API_BASE = (document.querySelector('meta[name="medowa-task-api"]')?.content || window.location.origin).replace(/\/+$/, '');

const money = new Intl.NumberFormat('en-IN', {
  style: 'currency',
  currency: 'INR',
  maximumFractionDigits: 0,
});

const app = document.getElementById('app');
const categoryNav = document.getElementById('category-nav');
const toastEl = document.getElementById('toast');

const cache = { categories: null, banners: null };

let toastTimer = null;

function notify(message) {
  toastEl.textContent = message;
  toastEl.classList.add('is-visible');
  window.clearTimeout(toastTimer);
  toastTimer = window.setTimeout(() => {
    toastEl.classList.remove('is-visible');
  }, 2200);
}

async function fetchJSON(path) {
  const response = await fetch(API_BASE + path, {
    headers: { Accept: 'application/json' },
  });
  if (!response.ok) {
    throw new Error('Request to ' + path + ' failed with status ' + response.status);
  }
  return response.json();
}

async function getCategories() {
  if (!cache.categories) {
    cache.categories = await fetchJSON('/api/categories/');
  }
  return cache.categories;
}

async function getBanners() {
  if (!cache.banners) {
    cache.banners = await fetchJSON('/api/banners/');
  }
  return cache.banners;
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) {
    node.className = className;
  }
  if (text !== undefined && text !== null) {
    node.textContent = text;
  }
  return node;
}

function moneyText(value) {
  const amount = Number(value);
  return Number.isFinite(amount) ? money.format(amount) : String(value);
}

function reference(id) {
  return 'CS-' + String(id).padStart(4, '0');
}

function statePanel(title, text, actionLabel, actionHref) {
  const panel = el('div', 'state-panel');
  panel.append(el('p', 'state-title', title));
  panel.append(el('p', 'state-text', text));
  if (actionLabel && actionHref) {
    const action = el('a', 'btn btn-secondary', actionLabel);
    action.href = actionHref;
    panel.append(action);
  }
  return panel;
}

function skeleton() {
  const grid = el('div', 'skeleton-grid');
  for (let index = 0; index < 8; index += 1) {
    grid.append(el('div', 'skeleton-card'));
  }
  return grid;
}

function productCard(product) {
  const card = el('a', 'product-card');
  card.href = '#/product/' + product.id;
  const media = el('div', 'product-media');
  const image = el('img');
  image.src = product.image;
  image.alt = product.name;
  image.loading = 'lazy';
  media.append(image);
  const body = el('div', 'product-body');
  body.append(el('p', 'product-category', product.category ? product.category.name : ''));
  body.append(el('h3', 'product-name', product.name));
  body.append(el('p', 'product-price', 'From ' + moneyText(product.price)));
  card.append(media, body);
  return card;
}

function heroSection(banner) {
  const hero = el('section', 'hero');
  hero.append(el('p', 'hero-eyebrow', 'Now available'));
  hero.append(el('h1', 'hero-title', banner.title));
  hero.append(el('p', 'hero-text', banner.subtitle));
  const actions = el('div', 'hero-actions');
  const shop = el('a', 'btn btn-primary', 'Shop now');
  shop.href = '#/';
  const browse = el('a', 'btn btn-secondary', 'Browse all models');
  browse.href = '#/';
  actions.append(shop, browse);
  hero.append(actions);
  const media = el('div', 'hero-media');
  const image = el('img');
  image.src = banner.image;
  image.alt = banner.title;
  media.append(image);
  hero.append(media);
  return hero;
}

function tileSection(banners) {
  const section = el('section', 'tiles');
  banners.forEach((banner) => {
    const tile = el('article', 'tile');
    const body = el('div', 'tile-body');
    body.append(el('h2', 'tile-title', banner.title));
    body.append(el('p', 'tile-text', banner.subtitle));
    const link = el('a', 'tile-link', 'Shop now \u203a');
    link.href = '#/';
    body.append(link);
    const media = el('div', 'tile-media');
    const image = el('img');
    image.src = banner.image;
    image.alt = banner.title;
    image.loading = 'lazy';
    media.append(image);
    tile.append(body, media);
    section.append(tile);
  });
  return section;
}

function pills(categories, activeSlug) {
  const wrap = el('div', 'pills');
  const all = el('a', 'pill' + (activeSlug ? '' : ' is-active'), 'All');
  all.href = '#/';
  wrap.append(all);
  categories.forEach((category) => {
    const link = el('a', 'pill' + (activeSlug === category.slug ? ' is-active' : ''), category.name);
    link.href = '#/category/' + category.slug;
    wrap.append(link);
  });
  return wrap;
}

function catalogHead(categories, activeSlug) {
  const head = el('div', 'section-head');
  const left = el('div');
  const active = categories.find((category) => category.slug === activeSlug);
  const title = activeSlug ? (active ? active.name : activeSlug) : 'The latest';
  left.append(el('h2', 'section-title', title));
  left.append(el('p', 'section-text', activeSlug ? 'Everything in ' + title + '.' : 'Take your pick from the new lineup.'));
  head.append(left, pills(categories, activeSlug));
  return head;
}

function detailRow(label, value) {
  const row = el('div', 'detail-row');
  row.append(el('dt', null, label));
  row.append(el('dd', null, value));
  return row;
}

function renderNav(categories, activeSlug) {
  categoryNav.replaceChildren();
  const store = el('a', 'nav-link' + (activeSlug ? '' : ' is-active'), 'Store');
  store.href = '#/';
  categoryNav.append(store);
  categories.forEach((category) => {
    const link = el('a', 'nav-link' + (activeSlug === category.slug ? ' is-active' : ''), category.name);
    link.href = '#/category/' + category.slug;
    categoryNav.append(link);
  });
}

async function renderCatalog(activeSlug) {
  app.replaceChildren(skeleton());
  try {
    const [categories, banners, products] = await Promise.all([
      getCategories(),
      getBanners(),
      fetchJSON('/api/products/' + (activeSlug ? '?category=' + encodeURIComponent(activeSlug) : '')),
    ]);
    renderNav(categories.results, activeSlug);
    const fragment = document.createDocumentFragment();
    if (!activeSlug) {
      if (banners.results.length) {
        fragment.append(heroSection(banners.results[0]));
      }
      const tiles = banners.results.slice(1, 3);
      if (tiles.length) {
        fragment.append(tileSection(tiles));
      }
    }
    fragment.append(catalogHead(categories.results, activeSlug));
    if (products.results.length) {
      const grid = el('div', 'product-grid');
      products.results.forEach((product) => grid.append(productCard(product)));
      fragment.append(grid);
    } else {
      fragment.append(statePanel('No products here yet', 'Try another category from the lineup.', 'Back to store', '#/'));
    }
    app.replaceChildren(fragment);
  } catch (error) {
    renderNav(cache.categories ? cache.categories.results : [], activeSlug);
    app.replaceChildren(statePanel('We could not load the catalog', error.message, 'Reload the store', '#/'));
  }
}

async function renderProduct(id) {
  app.replaceChildren(skeleton());
  try {
    const product = await fetchJSON('/api/products/' + id + '/');
    if (cache.categories) {
      renderNav(cache.categories.results, null);
    }
    const fragment = document.createDocumentFragment();
    const back = el('a', 'back-link', '\u2190 Back to store');
    back.href = '#/';
    fragment.append(back);

    const detail = el('section', 'product-detail');

    const media = el('div', 'detail-media');
    const image = el('img');
    image.src = product.image;
    image.alt = product.name;
    media.append(image);

    const info = el('div', 'detail-info');
    info.append(el('p', 'product-category', product.category.name));
    info.append(el('h1', 'detail-title', product.name));
    info.append(el('p', 'detail-price', 'MRP ' + moneyText(product.price)));
    info.append(el('p', 'detail-note', 'Inclusive of all taxes. Free delivery and free returns.'));
    info.append(el('p', 'detail-description', product.description));

    const rows = el('dl', 'detail-rows');
    rows.append(detailRow('Availability', 'In stock'));
    rows.append(detailRow('Collection', product.category.name));
    rows.append(detailRow('Item reference', reference(product.id)));
    info.append(rows);

    const actions = el('div', 'detail-actions');
    const add = el('button', 'btn btn-primary', 'Add to Bag');
    add.type = 'button';
    add.addEventListener('click', () => notify('Added ' + product.name + ' to the Bag'));
    const browse = el('a', 'btn btn-secondary', 'Continue shopping');
    browse.href = '#/';
    actions.append(add, browse);
    info.append(actions);

    detail.append(media, info);
    fragment.append(detail);
    app.replaceChildren(fragment);
  } catch (error) {
    app.replaceChildren(statePanel('Product unavailable', 'This product is no longer in the lineup.', 'Back to store', '#/'));
  }
}

const routes = [
  {
    pattern: /^#\/?$/,
    handler: () => renderCatalog(null),
  },
  {
    pattern: /^#\/category\/([A-Za-z0-9_-]+)$/,
    handler: (match) => renderCatalog(match[1]),
  },
  {
    pattern: /^#\/product\/(\d+)$/,
    handler: (match) => renderProduct(match[1]),
  },
];

function resolve() {
  const hash = window.location.hash || '#/';
  window.scrollTo({ top: 0, behavior: 'auto' });
  for (const route of routes) {
    const match = hash.match(route.pattern);
    if (match) {
      route.handler(match);
      return;
    }
  }
  window.location.hash = '#/';
}

function start() {
  renderNav([], null);
  window.addEventListener('hashchange', resolve);
  resolve();
}

start();
