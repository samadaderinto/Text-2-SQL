// Temporary visual harness. Actual screen components, synthetic data, no network.
import ReactDOM from 'react-dom/client';
import { MemoryRouter } from 'react-router-dom';
import { ToastContainer } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './styles/main.scss';
import api from './utils/api';
import { AuthProvider } from './contexts/auth-context';
import { Dashboard } from './components/Dashboard';
import { Product } from './components/Product';
import { Orders } from './components/Orders';
import { Customers } from './components/Customers';
import { NewProduct } from './components/NewProduct';
import { NewCustomer } from './components/NewCustomer';
import { Settings } from './components/Settings';
import Query from './components/Query';
import { SignIn } from './components/SignIn';
import { Signup } from './components/Signup';
import { ForgotPassword } from './components/ForgotPassword';
import { NewPassword } from './components/NewPassword';
import { Logout } from './components/Logout';
import { PageNotFound } from './pages/PageNotFound';
const params = new URLSearchParams(location.search);
const page = params.get('page') || 'dashboard';
const mode = params.get('mode') || 'populated';
const items = Array.from({length: 5}, (_, i) => ({
  id: 'order-00' + i, name: ['Jamie Brooks', 'Morgan Rivera', 'Taylor Chen'][i % 3],
  title: i === 0 ? 'Studio headphones with a very long product title' : 'Studio headphones',
  category: 'Electronics', status: ['paid','pending','cancelled'][i % 3],
  subtotal: String(89 + i * 43), price: '89.00', sales: i + 2, available: 12,
  created: '2026-10-04T12:00:00Z', first_name: 'Jamie', last_name: 'Brooks',
  email: i === 0 ? 'long.customer.email.address@example.com' : 'jamie@example.com'
}));
api.defaults.adapter = async config => {
  if (mode === 'loading' && config.url?.includes('search')) await new Promise(() => {});
  if (mode === 'error' && config.url?.includes('search')) throw new Error('Synthetic audit error');
  const records = mode === 'empty' ? [] : items;
  const data = config.url?.includes('/store/') ? {name:'Studio Supply', email:'store@example.com', currency:'$', user:1}
    : config.url?.includes('/admin/') ? {first_name:'Jamie', email:'jamie@example.com'}
    : config.url?.includes('/notifications/') ? {email_notification:true, push_notification:false}
    : {orders:records, products:records, customers:records, count:records.length};
  return {data,status:200,statusText:'OK',headers:{},config};
};
const screens: Record<string, JSX.Element> = {
  dashboard:<Dashboard/>, product:<Product/>, orders:<Orders/>, customers:<Customers/>,
  'product/add':<NewProduct/>, 'customers/add':<NewCustomer/>, settings:<Settings/>,
  query:<Query/>, signin:<SignIn/>, signup:<Signup/>, forgot:<ForgotPassword/>,
  reset:<NewPassword/>, logout:<Logout/>, missing:<PageNotFound/>
};
ReactDOM.createRoot(document.getElementById('root')!).render(
  <MemoryRouter initialEntries={[{pathname:'/'+page, state:page==='query' && mode==='populated' ? {queryResponse:{results:items, transcript:'Show recent orders', message:'Five records found', sql_preview:'SELECT * FROM orders LIMIT 5;', plan:{resource:'orders',intent:'search',limit:5}}} : undefined}]}>
    <AuthProvider><ToastContainer position="bottom-right" hideProgressBar />{screens[page]}</AuthProvider>
  </MemoryRouter>
);
