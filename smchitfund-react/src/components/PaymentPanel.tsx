import React, { useState, useEffect } from 'react';
import {
  Box,
  TextField,
  Button,
  Typography,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  InputAdornment,
  Stack,
  Alert,
  CircularProgress
} from '@mui/material';
import CurrencyRupeeIcon from '@mui/icons-material/CurrencyRupee';
import PaymentIcon from '@mui/icons-material/Payment';
import CancelIcon from '@mui/icons-material/Cancel';
import ApiService from '../services/api.service';

interface ChitItem {
  id: string;
  name: string;
  description?: string;
}

interface PaymentPanelProps {
  onPaymentSubmit: (paymentData: PaymentData) => void;
  onCancel: () => void;
}

export interface PaymentData {
  chitId: string;
  baseAmount: number;
  payAmount: number;
}

const PaymentPanel: React.FC<PaymentPanelProps> = ({ 
  onPaymentSubmit, 
  onCancel
}) => {
  // State for form fields
  const [selectedChit, setSelectedChit] = useState<string>('');
  const [baseAmount, setBaseAmount] = useState<number>(200);
  const [payAmount, setPayAmount] = useState<number>(200);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [availableChits, setAvailableChits] = useState<ChitItem[]>([]);

  // Fetch chit list when component mounts
  useEffect(() => {
    const fetchChitList = async () => {
      try {
        setLoading(true);
        const response = await ApiService.get('/chits');
        if (response.error) {
          setError('Failed to load chit list');
          setAvailableChits([]);
        } else {
          setAvailableChits(response.data || []);
          setError(null);
        }
      } catch (error) {
        console.error('Error fetching chit list:', error);
        setError('Failed to load chit list');
        setAvailableChits([]);
      } finally {
        setLoading(false);
      }
    };

    fetchChitList();
  }, []);
  
  // Update pay amount when base amount changes
  useEffect(() => {
    setPayAmount(baseAmount);
  }, [baseAmount]);

  // Handle chit selection change
  const handleChitChange = (event: SelectChangeEvent) => {
    setSelectedChit(event.target.value);
  };

  // Handle base amount change with validation
  const handleBaseAmountChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(event.target.value, 10);
    
    // If empty or not a number, set to minimum
    if (isNaN(value)) {
      setBaseAmount(200);
      return;
    }
    
    // Validate for minimum amount
    if (value < 200) {
      setBaseAmount(200);
      setError('Base amount must be at least ₹200');
      return;
    }
    
    // Validate for hundreds (200, 300, 400, etc.)
    if (value % 100 !== 0) {
      setBaseAmount(Math.floor(value / 100) * 100);
      setError('Base amount must be in hundreds (200, 300, 400, etc.)');
      return;
    }
    
    // Valid amount
    setBaseAmount(value);
    setError(null);
  };

  // Handle pay amount change
  const handlePayAmountChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = parseInt(event.target.value, 10);
    
    // If empty or not a number, set to base amount
    if (isNaN(value)) {
      setPayAmount(baseAmount);
      return;
    }
    
    // Validate for minimum amount (base amount)
    if (value < baseAmount) {
      setPayAmount(baseAmount);
      setError(`Pay amount must be at least ₹${baseAmount}`);
      return;
    }
    
    // Valid amount
    setPayAmount(value);
    setError(null);
  };

  // Handle form submission
  const handleSubmit = () => {
    // Validate form
    if (!selectedChit) {
      setError('Please select a chit');
      return;
    }
    
    if (baseAmount < 200) {
      setError('Base amount must be at least ₹200');
      return;
    }
    
    if (payAmount < baseAmount) {
      setError(`Pay amount must be at least ₹${baseAmount}`);
      return;
    }
    
    // Submit payment data
    onPaymentSubmit({
      chitId: selectedChit,
      baseAmount,
      payAmount
    });
  };

  return (
    <Paper elevation={3} sx={{ p: 3, width: '100%', maxWidth: 400 }}>
      <Typography variant="h6" component="h2" gutterBottom>
        Payment Details
      </Typography>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <Stack spacing={3}>
        {/* Chit Selection Dropdown */}
        <FormControl fullWidth>
          <InputLabel id="chit-select-label">Select Chit</InputLabel>
          <Select
            labelId="chit-select-label"
            id="chit-select"
            value={selectedChit}
            label="Select Chit"
            onChange={handleChitChange}
            required
            disabled={loading}
          >
            {loading ? (
              <MenuItem value="" disabled>
                Loading chits...
              </MenuItem>
            ) : availableChits.length === 0 ? (
              <MenuItem value="" disabled>
                No chits available
              </MenuItem>
            ) : (
              availableChits.map((chit) => (
                <MenuItem key={chit.id} value={chit.id}>
                  {chit.name}
                </MenuItem>
              ))
            )}
          </Select>
        </FormControl>
        
        {/* Base Amount Field */}
        <TextField
          fullWidth
          label="Base Amount"
          type="number"
          value={baseAmount}
          onChange={handleBaseAmountChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <CurrencyRupeeIcon />
              </InputAdornment>
            ),
          }}
          helperText="Minimum ₹200, in hundreds only (200, 300, 400, etc.)"
          required
        />
        
        {/* Pay Amount Field */}
        <TextField
          fullWidth
          label="Pay Amount"
          type="number"
          value={payAmount}
          onChange={handlePayAmountChange}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <CurrencyRupeeIcon />
              </InputAdornment>
            ),
          }}
          helperText={`Minimum ₹${baseAmount}`}
          required
        />
        
        {/* Action Buttons */}
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 2 }}>
          <Button
            variant="contained"
            color="primary"
            startIcon={loading ? <CircularProgress size={20} /> : <PaymentIcon />}
            onClick={handleSubmit}
            disabled={loading}
          >
            Pay Now
          </Button>
          
          <Button
            variant="outlined"
            color="secondary"
            startIcon={<CancelIcon />}
            onClick={onCancel}
            disabled={loading}
          >
            Cancel
          </Button>
        </Box>
      </Stack>
    </Paper>
  );
};

export default PaymentPanel;