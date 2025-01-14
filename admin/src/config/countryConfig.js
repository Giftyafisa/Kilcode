export const countryConfigs = {
  US: {
    currency: {
      code: 'USD',
      name: 'US Dollar',
      symbol: '$'
    }
  },
  GB: {
    currency: {
      code: 'GBP',
      name: 'British Pound',
      symbol: '£'
    }
  },
  EU: {
    currency: {
      code: 'EUR',
      name: 'Euro',
      symbol: '€'
    }
  },
  JP: {
    currency: {
      code: 'JPY',
      name: 'Japanese Yen',
      symbol: '¥'
    }
  }
};

export const getCountryConfig = (countryCode) => {
  return countryConfigs[countryCode] || null;
}; 