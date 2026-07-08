class ShopifyClient {
  constructor() {
    this.apiUrl = CONFIG.apiUrl;
    this.headers = {
      'Content-Type': 'application/json',
      'X-Shopify-Storefront-Access-Token': CONFIG.storefrontToken
    };
  }

  async query(query, variables = {}) {
    const res = await fetch(this.apiUrl, {
      method: 'POST',
      headers: this.headers,
      body: JSON.stringify({ query, variables })
    });
    const data = await res.json();
    if (data.errors) throw new Error(data.errors[0].message);
    return data.data;
  }

  async getProducts(first = 50) {
    const q = `
      {
        products(first: ${first}, sortKey: CREATED_AT, reverse: true) {
          edges {
            node {
              id
              title
              handle
              description
              productType
              tags
              priceRange { minVariantPrice { amount currencyCode } }
              images(first: 1) { edges { node { url altText width height } } }
            }
          }
        }
      }
    `;
    const data = await this.query(q);
    return data.products.edges.map(e => e.node);
  }

  async getCollections(first = 20) {
    const q = `
      {
        collections(first: ${first}) {
          edges {
            node {
              id
              title
              handle
              description
              image { url }
              products(first: 50) {
                edges { node { id title handle priceRange { minVariantPrice { amount } } images(first:1) { edges { node { url } } } } }
              }
            }
          }
        }
      }
    `;
    const data = await this.query(q);
    return data.collections.edges.map(e => e.node);
  }

  async getProductByHandle(handle) {
    const q = `
      {
        productByHandle(handle: "${handle}") {
          id
          title
          handle
          description
          descriptionHtml
          productType
          tags
          availableForSale
          priceRange { minVariantPrice { amount currencyCode } }
          images(first: 5) { edges { node { url altText width height } } }
          variants(first: 10) {
            edges {
              node {
                id
                title
                price { amount currencyCode }
                availableForSale
                selectedOptions { name value }
              }
            }
          }
        }
      }
    `;
    const data = await this.query(q);
    return data.productByHandle;
  }

  async createCart(variantId, quantity = 1) {
    const q = `
      mutation {
        cartCreate(input: { lines: [{ merchandiseId: "${variantId}", quantity: ${quantity} }] }) {
          cart { id checkoutUrl }
        }
      }
    `;
    const data = await this.query(q);
    return data.cartCreate.cart;
  }

  async getCart(cartId) {
    const q = `{ cart(id: "${cartId}") { id checkoutUrl totalQuantity cost { totalAmount { amount currencyCode } } lines(first: 20) { edges { node { quantity merchandise { ... on ProductVariant { id title price { amount } product { title images(first:1) { edges { node { url } } } } } } } } } } }`;
    const data = await this.query(q);
    return data.cart;
  }

  formatPrice(amount, currency = 'EUR') {
    return new Intl.NumberFormat('fr-FR', { style: 'currency', currency }).format(parseFloat(amount));
  }
}

const shopify = new ShopifyClient();
