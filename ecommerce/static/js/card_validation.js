function validateCardInput(cardData) {
    const errors = [];
    
    // Validate expiry
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear();
    const currentMonth = currentDate.getMonth() + 1; // JS months are 0-11
    
    if (cardData.exp_month < 1 || cardData.exp_month > 12) {
      errors.push("Invalid expiration month");
    }
    
    if (cardData.exp_year < currentYear || 
       (cardData.exp_year == currentYear && cardData.exp_month < currentMonth)) {
      errors.push("Card has expired");
    }
    
    // Two-digit year conversion
    if (cardData.exp_year < 100) {
      cardData.exp_year = 2000 + parseInt(cardData.exp_year);
    }
    
    return {
      isValid: errors.length === 0,
      errors,
      normalizedData: cardData
    };
  }