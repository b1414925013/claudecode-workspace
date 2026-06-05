export interface Account {
  id: number
  name: string
  account_type: string
  created_at: string
}

export interface Position {
  id: number
  account_id: number
  stock_code: string
  stock_name: string
  quantity: number
  avg_cost: number
  current_price?: number
  change_value?: number
  change_percent?: number
  market_value?: number
  created_at: string
  updated_at: string
}

export interface StockPrice {
  id: number
  stock_code: string
  price: number
  change_value?: number
  change_percent?: number
  trade_date: string
  created_at: string
}

export interface Trade {
  id: number
  account_id: number
  stock_code: string
  stock_name: string
  trade_type: string
  quantity: number
  price: number
  commission: number
  trade_date: string
  profit?: number
  created_at: string
}

export interface Dividend {
  id: number
  account_id: number
  stock_code: string
  stock_name: string
  dividend_amount: number
  dividend_date: string
  created_at: string
}

export interface Statistics {
  total_profit: number
  total_cost: number
  total_market_value: number
  return_rate: number
  win_rate: number
  total_trades: number
  winning_trades: number
  losing_trades: number
  avg_holding_days: number
}

export interface Summary {
  total_accounts: number
  total_positions: number
  total_trades: number
  total_cost: number
  total_profit: number
}