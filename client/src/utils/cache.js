class Cache {
    constructor() {
      this.store = {};
    }

    setData(key, value) {
      this.store[key] = value;
    }

    getData(key) {
      return this.store[key];
    }

    clear() {
      this.store = {};
    }
  }

  const cache = new Cache();
  export default cache;
