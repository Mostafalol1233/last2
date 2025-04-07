// Advanced Calculator Functions

// Scientific Calculator Functions
function addToDisplay(value) {
    document.getElementById('display').value += value;
}

function clearDisplay() {
    document.getElementById('display').value = '';
    document.getElementById('result').innerHTML = '';
}

function clearLastChar() {
    let display = document.getElementById('display');
    display.value = display.value.slice(0, -1);
}

function calculate() {
    try {
        let expression = document.getElementById('display').value;
        
        // Replace special functions with JavaScript Math equivalents
        expression = expression.replace(/sin\(/g, 'Math.sin(');
        expression = expression.replace(/cos\(/g, 'Math.cos(');
        expression = expression.replace(/tan\(/g, 'Math.tan(');
        expression = expression.replace(/log\(/g, 'Math.log10(');
        expression = expression.replace(/ln\(/g, 'Math.log(');
        expression = expression.replace(/sqrt\(/g, 'Math.sqrt(');
        expression = expression.replace(/abs\(/g, 'Math.abs(');
        expression = expression.replace(/π/g, 'Math.PI');
        expression = expression.replace(/e/g, 'Math.E');
        
        // Handle inverse trigonometric functions
        expression = expression.replace(/asin\(/g, 'Math.asin(');
        expression = expression.replace(/acos\(/g, 'Math.acos(');
        expression = expression.replace(/atan\(/g, 'Math.atan(');
        
        // Handle power function
        expression = expression.replace(/\^/g, '**');
        
        // Handle factorial
        while (expression.includes('!')) {
            const factRegex = /(\d+)!/;
            const match = expression.match(factRegex);
            if (match) {
                const num = parseInt(match[1]);
                const factorial = calculateFactorial(num);
                expression = expression.replace(match[0], factorial);
            } else {
                break;
            }
        }

        const result = eval(expression);
        document.getElementById('result').innerHTML = `Result: ${result}`;
    } catch (error) {
        document.getElementById('result').innerHTML = `Error: ${error.message}`;
    }
}

function calculateFactorial(n) {
    if (n === 0 || n === 1) {
        return 1;
    }
    let result = 1;
    for (let i = 2; i <= n; i++) {
        result *= i;
    }
    return result;
}

// Matrix Calculator Functions
function calculateMatrix() {
    try {
        const matrixA = parseMatrix(document.getElementById('matrix-a').value);
        const operation = document.getElementById('matrix-operation').value;
        let result = '';
        
        switch (operation) {
            case 'det':
                result = calculateDeterminant(matrixA);
                break;
            case 'inverse':
                result = calculateInverse(matrixA);
                break;
            case 'transpose':
                result = calculateTranspose(matrixA);
                break;
            case 'add':
            case 'multiply':
                const matrixB = parseMatrix(document.getElementById('matrix-b').value);
                if (operation === 'add') {
                    result = addMatrices(matrixA, matrixB);
                } else {
                    result = multiplyMatrices(matrixA, matrixB);
                }
                break;
        }
        
        document.getElementById('matrix-result').innerHTML = result;
    } catch (error) {
        document.getElementById('matrix-result').innerHTML = `Error: ${error.message}`;
    }
}

function parseMatrix(text) {
    // Split by lines and remove empty lines
    const rows = text.trim().split('\n').filter(row => row.trim() !== '');
    const matrix = rows.map(row => {
        // Split by spaces and convert to numbers
        const values = row.trim().split(/\s+/).map(val => parseFloat(val));
        return values;
    });
    
    // Validate matrix
    const rowLength = matrix[0].length;
    for (let i = 1; i < matrix.length; i++) {
        if (matrix[i].length !== rowLength) {
            throw new Error('All rows must have the same number of elements');
        }
    }
    
    return matrix;
}

function calculateDeterminant(matrix) {
    // Check if matrix is square
    if (matrix.length !== matrix[0].length) {
        throw new Error('Determinant can only be calculated for square matrices');
    }
    
    const n = matrix.length;
    
    // For 1x1 matrix
    if (n === 1) {
        return `Determinant = ${matrix[0][0]}`;
    }
    
    // For 2x2 matrix
    if (n === 2) {
        const det = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0];
        return `Determinant = ${det}`;
    }
    
    // For larger matrices, use recursive method
    let det = 0;
    for (let j = 0; j < n; j++) {
        det += matrix[0][j] * cofactor(matrix, 0, j);
    }
    
    return `Determinant = ${det}`;
}

function cofactor(matrix, row, col) {
    const minor = getMinor(matrix, row, col);
    const minorDet = determinant(minor);
    return Math.pow(-1, row + col) * minorDet;
}

function getMinor(matrix, row, col) {
    const minor = [];
    const n = matrix.length;
    
    for (let i = 0; i < n; i++) {
        if (i === row) continue;
        const newRow = [];
        for (let j = 0; j < n; j++) {
            if (j === col) continue;
            newRow.push(matrix[i][j]);
        }
        minor.push(newRow);
    }
    
    return minor;
}

function determinant(matrix) {
    const n = matrix.length;
    
    // For 1x1 matrix
    if (n === 1) {
        return matrix[0][0];
    }
    
    // For 2x2 matrix
    if (n === 2) {
        return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0];
    }
    
    // For larger matrices, use recursive method
    let det = 0;
    for (let j = 0; j < n; j++) {
        det += matrix[0][j] * cofactor(matrix, 0, j);
    }
    
    return det;
}

function calculateInverse(matrix) {
    // Check if matrix is square
    if (matrix.length !== matrix[0].length) {
        throw new Error('Inverse can only be calculated for square matrices');
    }
    
    const n = matrix.length;
    const det = determinant(matrix);
    
    if (Math.abs(det) < 1e-10) {
        throw new Error('Matrix is singular (determinant is zero), inverse does not exist');
    }
    
    // For 1x1 matrix
    if (n === 1) {
        const inverse = [[1 / matrix[0][0]]];
        return formatMatrix(inverse);
    }
    
    // For larger matrices
    const cofactorMatrix = [];
    for (let i = 0; i < n; i++) {
        cofactorMatrix[i] = [];
        for (let j = 0; j < n; j++) {
            cofactorMatrix[i][j] = cofactor(matrix, i, j);
        }
    }
    
    // Transpose of cofactor matrix
    const adjugate = calculateTransposeMatrix(cofactorMatrix);
    
    // Multiply by 1/determinant
    const inverse = [];
    for (let i = 0; i < n; i++) {
        inverse[i] = [];
        for (let j = 0; j < n; j++) {
            inverse[i][j] = adjugate[i][j] / det;
        }
    }
    
    return formatMatrix(inverse);
}

function calculateTranspose(matrix) {
    const transposed = calculateTransposeMatrix(matrix);
    return formatMatrix(transposed);
}

function calculateTransposeMatrix(matrix) {
    const rows = matrix.length;
    const cols = matrix[0].length;
    const transposed = [];
    
    for (let j = 0; j < cols; j++) {
        transposed[j] = [];
        for (let i = 0; i < rows; i++) {
            transposed[j][i] = matrix[i][j];
        }
    }
    
    return transposed;
}

function addMatrices(matrixA, matrixB) {
    // Check if matrices have the same dimensions
    if (matrixA.length !== matrixB.length || matrixA[0].length !== matrixB[0].length) {
        throw new Error('Matrices must have the same dimensions for addition');
    }
    
    const rows = matrixA.length;
    const cols = matrixA[0].length;
    const result = [];
    
    for (let i = 0; i < rows; i++) {
        result[i] = [];
        for (let j = 0; j < cols; j++) {
            result[i][j] = matrixA[i][j] + matrixB[i][j];
        }
    }
    
    return formatMatrix(result);
}

function multiplyMatrices(matrixA, matrixB) {
    // Check if matrices can be multiplied
    if (matrixA[0].length !== matrixB.length) {
        throw new Error('Number of columns in first matrix must equal number of rows in second matrix');
    }
    
    const rowsA = matrixA.length;
    const colsA = matrixA[0].length;
    const colsB = matrixB[0].length;
    const result = [];
    
    for (let i = 0; i < rowsA; i++) {
        result[i] = [];
        for (let j = 0; j < colsB; j++) {
            result[i][j] = 0;
            for (let k = 0; k < colsA; k++) {
                result[i][j] += matrixA[i][k] * matrixB[k][j];
            }
        }
    }
    
    return formatMatrix(result);
}

function formatMatrix(matrix) {
    let formattedResult = '<div class="matrix-result-container">';
    for (let i = 0; i < matrix.length; i++) {
        formattedResult += '<div class="matrix-row">';
        for (let j = 0; j < matrix[i].length; j++) {
            // Format number to handle floating point precision issues
            const value = parseFloat(matrix[i][j].toFixed(4));
            formattedResult += `<span class="matrix-cell">${value}</span>`;
        }
        formattedResult += '</div>';
    }
    formattedResult += '</div>';
    return formattedResult;
}

// Unit Converter Functions
function updateFromUnit() {
    const unitType = document.getElementById('unit-type').value;
    const fromUnitSelect = document.getElementById('from-unit');
    const toUnitSelect = document.getElementById('to-unit');
    
    // Clear existing options
    fromUnitSelect.innerHTML = '';
    toUnitSelect.innerHTML = '';
    
    // Add appropriate options based on unit type
    switch (unitType) {
        case 'length':
            addUnitOptions(fromUnitSelect, toUnitSelect, {
                'mm': 'Millimeter',
                'cm': 'Centimeter',
                'm': 'Meter',
                'km': 'Kilometer',
                'in': 'Inch',
                'ft': 'Foot',
                'yd': 'Yard',
                'mi': 'Mile'
            });
            break;
        case 'weight':
            addUnitOptions(fromUnitSelect, toUnitSelect, {
                'mg': 'Milligram',
                'g': 'Gram',
                'kg': 'Kilogram',
                'oz': 'Ounce',
                'lb': 'Pound',
                'ton': 'Metric Ton'
            });
            break;
        case 'area':
            addUnitOptions(fromUnitSelect, toUnitSelect, {
                'mm2': 'Square Millimeter',
                'cm2': 'Square Centimeter',
                'm2': 'Square Meter',
                'km2': 'Square Kilometer',
                'in2': 'Square Inch',
                'ft2': 'Square Foot',
                'ac': 'Acre',
                'ha': 'Hectare'
            });
            break;
        case 'volume':
            addUnitOptions(fromUnitSelect, toUnitSelect, {
                'ml': 'Milliliter',
                'l': 'Liter',
                'm3': 'Cubic Meter',
                'gal': 'Gallon (US)',
                'qt': 'Quart (US)',
                'pt': 'Pint (US)',
                'cup': 'Cup (US)',
                'oz_fl': 'Fluid Ounce (US)'
            });
            break;
        case 'temperature':
            addUnitOptions(fromUnitSelect, toUnitSelect, {
                'c': 'Celsius',
                'f': 'Fahrenheit',
                'k': 'Kelvin'
            });
            break;
    }
}

function addUnitOptions(fromSelect, toSelect, options) {
    for (const [value, label] of Object.entries(options)) {
        fromSelect.add(new Option(label, value));
        toSelect.add(new Option(label, value));
    }
}

function convertUnit() {
    const value = parseFloat(document.getElementById('unit-value').value);
    if (isNaN(value)) {
        document.getElementById('unit-result').innerHTML = 'Please enter a valid number';
        return;
    }
    
    const unitType = document.getElementById('unit-type').value;
    const fromUnit = document.getElementById('from-unit').value;
    const toUnit = document.getElementById('to-unit').value;
    
    let result;
    
    // Convert to base unit first, then to target unit
    switch (unitType) {
        case 'length':
            result = convertLength(value, fromUnit, toUnit);
            break;
        case 'weight':
            result = convertWeight(value, fromUnit, toUnit);
            break;
        case 'area':
            result = convertArea(value, fromUnit, toUnit);
            break;
        case 'volume':
            result = convertVolume(value, fromUnit, toUnit);
            break;
        case 'temperature':
            result = convertTemperature(value, fromUnit, toUnit);
            break;
    }
    
    document.getElementById('unit-result').innerHTML = `${value} ${fromUnit} = ${result.toFixed(6)} ${toUnit}`;
}

function convertLength(value, fromUnit, toUnit) {
    // Convert to meters first (base unit)
    const meterConversion = {
        'mm': 0.001,
        'cm': 0.01,
        'm': 1,
        'km': 1000,
        'in': 0.0254,
        'ft': 0.3048,
        'yd': 0.9144,
        'mi': 1609.344
    };
    
    // Convert input to meters
    const meters = value * meterConversion[fromUnit];
    
    // Convert meters to target unit
    return meters / meterConversion[toUnit];
}

function convertWeight(value, fromUnit, toUnit) {
    // Convert to grams first (base unit)
    const gramConversion = {
        'mg': 0.001,
        'g': 1,
        'kg': 1000,
        'oz': 28.3495,
        'lb': 453.592,
        'ton': 1000000
    };
    
    // Convert input to grams
    const grams = value * gramConversion[fromUnit];
    
    // Convert grams to target unit
    return grams / gramConversion[toUnit];
}

function convertArea(value, fromUnit, toUnit) {
    // Convert to square meters first (base unit)
    const squareMeterConversion = {
        'mm2': 0.000001,
        'cm2': 0.0001,
        'm2': 1,
        'km2': 1000000,
        'in2': 0.00064516,
        'ft2': 0.092903,
        'ac': 4046.86,
        'ha': 10000
    };
    
    // Convert input to square meters
    const squareMeters = value * squareMeterConversion[fromUnit];
    
    // Convert square meters to target unit
    return squareMeters / squareMeterConversion[toUnit];
}

function convertVolume(value, fromUnit, toUnit) {
    // Convert to liters first (base unit)
    const literConversion = {
        'ml': 0.001,
        'l': 1,
        'm3': 1000,
        'gal': 3.78541,
        'qt': 0.946353,
        'pt': 0.473176,
        'cup': 0.236588,
        'oz_fl': 0.0295735
    };
    
    // Convert input to liters
    const liters = value * literConversion[fromUnit];
    
    // Convert liters to target unit
    return liters / literConversion[toUnit];
}

function convertTemperature(value, fromUnit, toUnit) {
    // Temperature conversions are special cases
    let celsius;
    
    // Convert to Celsius first
    switch (fromUnit) {
        case 'c':
            celsius = value;
            break;
        case 'f':
            celsius = (value - 32) * 5/9;
            break;
        case 'k':
            celsius = value - 273.15;
            break;
    }
    
    // Convert Celsius to target unit
    switch (toUnit) {
        case 'c':
            return celsius;
        case 'f':
            return celsius * 9/5 + 32;
        case 'k':
            return celsius + 273.15;
    }
}

// Calculus Functions
function solveDerivative() {
    try {
        const functionText = document.getElementById('derivative-function').value;
        const variable = document.getElementById('derivative-variable').value || 'x';
        
        // Simple symbolic differentiation for polynomial functions
        // This is a basic implementation that works for simple polynomials
        const terms = parseFunctionTerms(functionText, variable);
        const derivedTerms = [];
        
        for (const term of terms) {
            if (term.hasVariable) {
                const coefficient = term.coefficient * term.exponent;
                const newExponent = term.exponent - 1;
                
                if (newExponent === 0) {
                    derivedTerms.push(`${coefficient}`);
                } else if (newExponent === 1) {
                    derivedTerms.push(`${coefficient}${variable}`);
                } else {
                    derivedTerms.push(`${coefficient}${variable}^${newExponent}`);
                }
            }
        }
        
        const derivativeResult = derivedTerms.join(' + ').replace(/\+ -/g, '- ');
        document.getElementById('derivative-result').innerHTML = `f'(${variable}) = ${derivativeResult || '0'}`;
    } catch (error) {
        document.getElementById('derivative-result').innerHTML = `Error: ${error.message}`;
    }
}

function parseFunctionTerms(functionText, variable) {
    // Replace minus signs with plus minus
    functionText = functionText.replace(/\s/g, '').replace(/-/g, '+-');
    if (functionText.startsWith('+')) {
        functionText = functionText.substring(1);
    }
    
    // Split by plus signs
    const termStrings = functionText.split('+');
    const terms = [];
    
    for (const termString of termStrings) {
        if (!termString) continue;
        
        let coefficient = 1;
        let exponent = 0;
        let hasVariable = false;
        
        // Check if term contains the variable
        if (termString.includes(variable)) {
            hasVariable = true;
            
            // Find coefficient
            if (termString.startsWith(variable)) {
                coefficient = 1;
            } else if (termString.startsWith('-' + variable)) {
                coefficient = -1;
            } else {
                const parts = termString.split(variable);
                coefficient = parseFloat(parts[0]);
            }
            
            // Find exponent
            if (termString.includes('^')) {
                const exponentPart = termString.split('^')[1];
                exponent = parseFloat(exponentPart);
            } else {
                exponent = 1;
            }
        } else {
            // Term is a constant
            coefficient = parseFloat(termString);
            exponent = 0;
        }
        
        terms.push({ coefficient, exponent, hasVariable });
    }
    
    return terms;
}

function solveIntegral() {
    try {
        const functionText = document.getElementById('integral-function').value;
        const variable = document.getElementById('integral-variable').value || 'x';
        const lowerBound = document.getElementById('integral-lower').value;
        const upperBound = document.getElementById('integral-upper').value;
        
        // Simple symbolic integration for polynomial functions
        // This is a basic implementation that works for simple polynomials
        const terms = parseFunctionTerms(functionText, variable);
        const integratedTerms = [];
        
        for (const term of terms) {
            if (term.hasVariable) {
                const newExponent = term.exponent + 1;
                const coefficient = term.coefficient / newExponent;
                
                integratedTerms.push(`${coefficient}${variable}^${newExponent}`);
            } else {
                // Constant term
                integratedTerms.push(`${term.coefficient}${variable}`);
            }
        }
        
        const integralResult = integratedTerms.join(' + ').replace(/\+ -/g, '- ') + ' + C';
        
        let definiteIntegralResult = '';
        // If bounds are provided, calculate the definite integral
        if (lowerBound && upperBound) {
            try {
                const lowerValue = calculateIntegralAtPoint(terms, parseFloat(lowerBound));
                const upperValue = calculateIntegralAtPoint(terms, parseFloat(upperBound));
                const result = upperValue - lowerValue;
                definiteIntegralResult = `Definite integral value from ${lowerBound} to ${upperBound} = ${result.toFixed(4)}`;
            } catch (e) {
                definiteIntegralResult = 'Could not calculate definite integral: ' + e.message;
            }
        }
        
        document.getElementById('integral-result').innerHTML = `∫${functionText} d${variable} = ${integralResult}<br>${definiteIntegralResult}`;
    } catch (error) {
        document.getElementById('integral-result').innerHTML = `Error: ${error.message}`;
    }
}

function calculateIntegralAtPoint(terms, point) {
    let result = 0;
    
    for (const term of terms) {
        if (term.hasVariable) {
            const newExponent = term.exponent + 1;
            const coefficient = term.coefficient / newExponent;
            result += coefficient * Math.pow(point, newExponent);
        } else {
            // Constant term
            result += term.coefficient * point;
        }
    }
    
    return result;
}

// Initialize event listeners when the document is ready
document.addEventListener('DOMContentLoaded', function() {
    // Initialize unit converter dropdown
    const unitTypeSelect = document.getElementById('unit-type');
    if (unitTypeSelect) {
        unitTypeSelect.addEventListener('change', updateFromUnit);
        // Initialize units on page load
        updateFromUnit();
    }
});