// Fetch and display exchange rates
async function fetchExchangeRates() {
    try {
        const response = await fetch('/api/rates/');
        const data = await response.json();

        // API returns array directly, not wrapped in {rates: [...]}
        if (Array.isArray(data) && data.length > 0) {
            // Filter out MMK (base currency) and only show foreign currencies
            const foreignRates = data.filter(rate => rate.currency_code !== 'MMK');

            if (foreignRates.length > 0) {
                displayPhoneRates(foreignRates);
                displayFullRates(foreignRates);
            } else {
                showError();
            }
        } else {
            showError();
        }
    } catch (error) {
        console.error('Error fetching rates:', error);
        showError();
    }
}

// Display rates in phone mockup
function displayPhoneRates(rates) {
    const container = document.getElementById('phone-rates-container');
    if (!container) return;

    // Show max 4 rates in phone mockup
    const displayRates = rates.slice(0, 4);

    container.innerHTML = displayRates.map(rate => `
        <div class="phone-rate-card">
            <div class="phone-rate-header">
                <div class="phone-currency-symbol">${getCurrencySymbol(rate.currency_code)}</div>
                <div class="phone-currency-info">
                    <h4>${rate.currency_code}</h4>
                    <p>${rate.currency_name}</p>
                </div>
            </div>
            <div class="phone-rate-values">
                <div class="phone-rate-item">
                    <div class="label">ဝယ်ယူမည်</div>
                    <div class="value">${formatRate(rate.buy_rate)}</div>
                </div>
                <div class="phone-rate-item">
                    <div class="label">ရောင်းမည်</div>
                    <div class="value">${formatRate(rate.sell_rate)}</div>
                </div>
            </div>
        </div>
    `).join('');
}

// Display full rates section
function displayFullRates(rates) {
    const loadingEl = document.getElementById('full-rates-loading');
    const containerEl = document.getElementById('full-rates-container');
    const errorEl = document.getElementById('rates-error');

    if (!containerEl) return;

    loadingEl.style.display = 'none';
    containerEl.style.display = 'grid';
    errorEl.style.display = 'none';

    containerEl.innerHTML = rates.map(rate => `
        <div class="rate-card">
            <div class="rate-header">
                <div class="currency-symbol">${getCurrencySymbol(rate.currency_code)}</div>
                <div class="currency-info">
                    <h3>${rate.currency_code}</h3>
                    <p>${rate.currency_name}</p>
                </div>
            </div>
            <div class="rate-values">
                <div class="rate-item">
                    <div class="label">ဝယ်ယူနှုန်း</div>
                    <div class="value">${formatRate(rate.buy_rate)} MMK</div>
                </div>
                <div class="rate-item">
                    <div class="label">ရောင်းချနှုန်း</div>
                    <div class="value">${formatRate(rate.sell_rate)} MMK</div>
                </div>
            </div>
        </div>
    `).join('');
}

// Show error message
function showError() {
    const phoneContainer = document.getElementById('phone-rates-container');
    const loadingEl = document.getElementById('full-rates-loading');
    const containerEl = document.getElementById('full-rates-container');
    const errorEl = document.getElementById('rates-error');

    if (phoneContainer) {
        phoneContainer.innerHTML = `
            <div class="phone-loading">
                <p style="color: #D32F2F;">Failed to load rates</p>
            </div>
        `;
    }

    if (loadingEl) loadingEl.style.display = 'none';
    if (containerEl) containerEl.style.display = 'none';
    if (errorEl) errorEl.style.display = 'block';
}

// Get currency symbol
function getCurrencySymbol(code) {
    const symbols = {
        'USD': '$',
        'THB': '฿',
        'SGD': 'S$',
        'EUR': '€',
        'GBP': '£',
        'JPY': '¥',
        'CNY': '¥',
        'KRW': '₩',
        'MYR': 'RM',
        'INR': '₹'
    };
    return symbols[code] || code;
}

// Format rate number
function formatRate(rate) {
    return parseFloat(rate).toLocaleString('en-US', {
        minimumFractionDigits: 2,
        maximumFractionDigits: 4
    });
}

// Auto-refresh rates every 60 seconds
let refreshInterval;

function startAutoRefresh() {
    refreshInterval = setInterval(fetchExchangeRates, 60000);
}

function stopAutoRefresh() {
    if (refreshInterval) {
        clearInterval(refreshInterval);
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    fetchExchangeRates();
    startAutoRefresh();
});

// Stop refresh when page is hidden
document.addEventListener('visibilitychange', () => {
    if (document.hidden) {
        stopAutoRefresh();
    } else {
        startAutoRefresh();
    }
});
