import { BrowserRouter } from 'react-router-dom'
import { ConfigProvider } from 'antd'
import AppRoutes from './routes/AppRoutes'

const antTheme = {
  token: {
    colorPrimary: '#38BDF8',
    colorBgBase: '#0A0F1C',
    colorTextBase: '#E8EDF5',
    borderRadius: 8,
    fontFamily: "'DM Sans', system-ui, sans-serif",
    fontSize: 14,
    colorBorder: '#1F2D44',
    colorBgContainer: '#111827',
    colorBgElevated: '#1A2235',
    colorError: '#F87171',
    colorSuccess: '#34D399',
    colorWarning: '#FBBF24',
    colorInfo: '#38BDF8',
  },
}

export default function App() {
  return (
    <ConfigProvider theme={antTheme}>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </ConfigProvider>
  )
}
