import { useState, useEffect, useContext } from "react";
import { HiOutlineChartSquareBar } from 'react-icons/hi';
import { RiShoppingBag4Line } from 'react-icons/ri';
import { GoContainer } from "react-icons/go";
import { IoPeopleOutline } from 'react-icons/io5';

import { DashboardCardProps } from "../types/dashboard";
import SideBar from "../layouts/SideBar";
import { Header } from "../layouts/Header";
import { Line, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, ArcElement, Tooltip, Legend } from 'chart.js';
import { AuthContext } from "../contexts/auth-context";
import { OrderProps } from "../types/order";
import api from "../utils/api";
import { useNavigate } from "react-router-dom";



ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, ArcElement, Tooltip, Legend);

export const Dashboard = () => {
  const { isSignedIn, user } = useContext(AuthContext);
  const [Active, setActive] = useState<number | null>(0);
  const [orders, setOrders] = useState<OrderProps[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const nav = useNavigate()

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        setLoading(true);
        const response = await api.get(`/orders/search/`);
        setOrders(response.data);
        setLoading(false);
      } catch (err) {
        setError("Failed to load orders.");
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  const cardArray: DashboardCardProps[] = [
    {
      icon: <HiOutlineChartSquareBar />,
      title: 'Total Sales',
      value: 271568.09,
      percent: 25.5,
      increment: 15,
    },
    {
      icon: <RiShoppingBag4Line />,
      title: 'Total Sale',
      value: 271568.09,
      percent: 25.5,
      increment: 15,
    },
    {
      icon: <GoContainer />,
      title: 'Total Sales',
      value: 271568.09,
      percent: 25.5,
      increment: 15,
    },
    {
      icon: <IoPeopleOutline />,
      title: 'Total Sale',
      value: 271568.09,
      percent: 25.5,
      increment: 15,
    },
  ];

  const salesData = {
    labels: [
      "January", "February", "March", "April", "May", "June",
      "July", "August", "September", "October", "November", "December"
    ],
    datasets: [
      {
        label: "Total Sales",
        data: [1200, 1900, 3000, 5000, 2400, 3400, 2900, 4700, 5200, 6000, 7000, 8000], // example data
        fill: false,
        backgroundColor: "blue",
        borderColor: "blue",
        tension: 0.1,
      },
    ],
  };

  const pieData = {
    labels: ['Product A', 'Product B', 'Product C', 'Product D'],
    datasets: [
      {
        label: 'Product Distribution',
        data: [300, 200, 100, 150], // example data
        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#E7E9ED'],
        borderColor: '#fff',
        borderWidth: 1,
      },
    ],
  };

  const options = {
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <>
      <Header />

      <div className="Dashboard_container">
        <SideBar />

        <h1>{isSignedIn ? <p>Welcome, {user?.email?.split("@")[0]}</p> : <p>Welcome</p>}</h1>
        <p>Here's what's happening with your store today.</p>

        <section className="Dashboard_Card_Container">
          {cardArray.map((obj, index) => (
            <article
              key={index}
              onClick={() => {
                setActive(index);
              }}
              className={Active === index ? 'Blue_Card' : ''}
            >
              <span>
                <div>{obj.icon}</div>
                <h4>{obj.title}</h4>
              </span>
              <h3>{obj.title === 'Total Sales' ? `$${obj.value}` : obj.value}</h3>
              <span>
                <p className="Card_percentage">{`${obj.percent}%`}</p>
                <p>{`+${obj.increment}k Today`}</p>
              </span>
            </article>
          ))}
        </section>

        <section className="Graph_Container">
          <div className="Main_Graph_Container">
            <span>
              <h3>Total Sales Over the Year</h3>
              <p onClick={()=> nav("/orders")}>View All</p>
            </span>

            <span className="Graph_Subheader">
              <h4>Name</h4>
              <ul>
                <li>ID</li>
                <li>Price</li>
                <li>Amount</li>
                <li>Status</li>
              </ul>
            </span>

            <article>
              {loading ? (
                <p>Loading orders...</p>
              ) : error ? (
                <p>{error}</p>
              ) : (
                orders.map((order) => (
                  <span key={order.orderId} className="Dashboard_Order_Item">
                    <div className="Dashboard_Order_Item_Description">
                      <span className="Item_Img_Holder">
                        <img src={order.image || ""} alt={order.productName} />
                      </span>
                      <span>
                        <h2>{order.productName}</h2>
                        <h4>{order.category}</h4>
                      </span>
                    </div>
                    <div>
                      <p>{order.orderId}</p>
                      <p>{order.amount}</p>
                      <p>{order.status}</p>
                    </div>
                  </span>
                ))
              )}
            </article>

            <Line data={salesData} options={options} />
          </div>
          <div className="Side_Graph_Container">
            <Pie data={pieData} />
          </div>
        </section>

        <section className="Bottom_Graph_Container"></section>
      </div>
    </>
  );
};
