"""
Danh sách top 100 cổ phiếu Việt Nam theo vốn hóa thị trường
"""

# Top 100 cổ phiếu VN-Index và HNX theo vốn hóa (cập nhật 2024)
TOP_100_STOCKS = [
    # Top VN30
    'VCB', 'VHM', 'VNM', 'VIC', 'GAS', 'MSN', 'HPG', 'TCB', 'FPT', 'MWG',
    'VPB', 'BID', 'CTG', 'MBB', 'SAB', 'VRE', 'HDB', 'PLX', 'VJC', 'NVL',
    'BCM', 'GVR', 'POW', 'ACB', 'SSI', 'STB', 'TPB', 'PDR', 'BVH', 'VHC',
    
    # Top midcap
    'VCI', 'DGC', 'KDH', 'DPM', 'DCM', 'VIB', 'VGC', 'HT1', 'PC1', 'MSB',
    'PVD', 'GMD', 'DBC', 'BWE', 'NT2', 'HSG', 'PNJ', 'DGW', 'VCS', 'HCM',
    'VHG', 'TCH', 'VTO', 'IDC', 'SZC', 'KBC', 'DXG', 'PVT', 'VSC', 'CTD',
    
    # Thêm các mã khác
    'HDG', 'LPB', 'OCB', 'VND', 'PVS', 'VGS', 'PAN', 'BMP', 'SBT', 'VSH',
    'HT1', 'PC1', 'KDC', 'PPC', 'GEX', 'DHC', 'SHB', 'REE', 'PVG', 'VCG',
    'AGG', 'DRC', 'HNG', 'VPI', 'EVF', 'QNS', 'NLG', 'KSB', 'HDC', 'SCS',
    'DVP', 'HTV', 'BFC', 'PPC', 'DPR', 'SRC', 'VNE', 'VDS', 'HAG', 'TNG'
]

# Phân loại theo ngành
SECTOR_MAPPING = {
    # Ngân hàng
    'Banking': ['VCB', 'TCB', 'BID', 'CTG', 'MBB', 'VPB', 'ACB', 'STB', 'TPB', 'HDB', 'VIB', 'LPB', 'OCB', 'SHB', 'MSB'],
    
    # Bất động sản
    'Real Estate': ['VHM', 'VIC', 'NVL', 'VRE', 'KDH', 'DXG', 'HDC', 'NLG', 'DIG', 'PDR', 'DRH', 'HDG', 'VHG', 'QCG'],
    
    # Chứng khoán
    'Securities': ['SSI', 'VCI', 'VND', 'HCM', 'MBS', 'SHS', 'FTS', 'VDS', 'AGR', 'BSI'],
    
    # Sản xuất & công nghiệp
    'Manufacturing': ['HPG', 'HSG', 'DGC', 'DCM', 'DPM', 'NT2', 'VCS', 'GEX', 'KBC', 'PAN'],
    
    # Công nghệ & viễn thông
    'Technology': ['FPT', 'VGI', 'ITD', 'CMG', 'SAM', 'ELC'],
    
    # Bán lẻ
    'Retail': ['MWG', 'PNJ', 'DGW', 'FRT'],
    
    # Thực phẩm & đồ uống
    'Food & Beverage': ['VNM', 'SAB', 'MSN', 'VHC', 'MCH', 'KDC', 'SBT'],
    
    # Năng lượng
    'Energy': ['GAS', 'POW', 'PLX', 'PVD', 'PVS', 'PVT', 'PVG', 'BSR', 'GEG'],
    
    # Xây dựng
    'Construction': ['CTD', 'HBC', 'FCN', 'HT1', 'PC1', 'CII', 'VCG'],
    
    # Khác
    'Others': ['BCM', 'GVR', 'BVH', 'GMD', 'DHC', 'REE', 'VTO', 'BMP']
}

def get_sector(symbol):
    """
    Lấy ngành của mã cổ phiếu
    
    Args:
        symbol: Mã cổ phiếu
    
    Returns:
        Tên ngành
    """
    for sector, stocks in SECTOR_MAPPING.items():
        if symbol in stocks:
            return sector
    return 'Others'

def get_stocks_by_sector(sector):
    """
    Lấy danh sách cổ phiếu theo ngành
    
    Args:
        sector: Tên ngành
    
    Returns:
        List các mã cổ phiếu
    """
    return SECTOR_MAPPING.get(sector, [])

def get_all_sectors():
    """
    Lấy danh sách tất cả các ngành
    
    Returns:
        List tên các ngành
    """
    return list(SECTOR_MAPPING.keys())

# VN30 - Top 30 cổ phiếu blue chip
VN30_STOCKS = [
    'VCB', 'VHM', 'VNM', 'VIC', 'GAS', 'MSN', 'HPG', 'TCB', 'FPT', 'MWG',
    'VPB', 'BID', 'CTG', 'MBB', 'SAB', 'VRE', 'HDB', 'PLX', 'VJC', 'NVL',
    'BCM', 'GVR', 'POW', 'ACB', 'SSI', 'STB', 'TPB', 'PDR', 'BVH', 'VHC'
]

# Midcap - Cổ phiếu vốn hóa trung bình
MIDCAP_STOCKS = [
    'VCI', 'DGC', 'KDH', 'DPM', 'DCM', 'VIB', 'VGC', 'HT1', 'PC1', 'MSB',
    'PVD', 'GMD', 'DBC', 'BWE', 'NT2', 'HSG', 'PNJ', 'DGW', 'VCS', 'HCM'
]

# Smallcap - Cổ phiếu vốn hóa nhỏ
SMALLCAP_STOCKS = [
    'HDG', 'LPB', 'OCB', 'VND', 'PVS', 'VGS', 'PAN', 'BMP', 'SBT', 'VSH',
    'KDC', 'PPC', 'GEX', 'DHC', 'SHB', 'REE', 'PVG', 'VCG', 'AGG', 'DRC'
]
