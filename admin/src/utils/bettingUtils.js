export const filterCodes = (codes, filters, searchTerm) => {
    let filtered = [...codes];

    // Apply search filter
    if (searchTerm) {
        filtered = filtered.filter(code => 
            code.user_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
            code.code.toLowerCase().includes(searchTerm.toLowerCase()) ||
            code.bookmaker.toLowerCase().includes(searchTerm.toLowerCase())
        );
    }

    // Apply status filter
    if (filters.status !== 'all') {
        filtered = filtered.filter(code => code.status === filters.status);
    }

    // Apply bookmaker filter
    if (filters.bookmaker !== 'all') {
        filtered = filtered.filter(code => code.bookmaker === filters.bookmaker);
    }

    // Apply date range filter
    if (filters.dateRange !== 'all') {
        const now = new Date();
        const past = new Date();
        
        switch (filters.dateRange) {
            case 'today':
                past.setDate(now.getDate() - 1);
                break;
            case 'week':
                past.setDate(now.getDate() - 7);
                break;
            case 'month':
                past.setMonth(now.getMonth() - 1);
                break;
        }
        
        filtered = filtered.filter(code => new Date(code.created_at) >= past);
    }

    return filtered;
};

export const sortCodes = (codes, sortConfig) => {
    return [...codes].sort((a, b) => {
        if (sortConfig.direction === 'asc') {
            return a[sortConfig.key] > b[sortConfig.key] ? 1 : -1;
        }
        return a[sortConfig.key] < b[sortConfig.key] ? 1 : -1;
    });
};

export const exportToCSV = (codes) => {
    const headers = [
        'User',
        'Bookmaker',
        'Code',
        'Odds',
        'Stake',
        'Potential Winnings',
        'Status',
        'Date'
    ];

    const csvContent = [
        headers.join(','),
        ...codes.map(code => [
            code.user_name,
            code.bookmaker,
            code.code,
            code.odds,
            code.stake,
            code.potential_winnings,
            code.status,
            new Date(code.created_at).toLocaleDateString()
        ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.href = URL.createObjectURL(blob);
    link.download = `betting_codes_${new Date().toISOString()}.csv`;
    link.click();
}; 