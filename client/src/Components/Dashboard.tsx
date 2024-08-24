import { useState } from "react";
import { HiOutlineChartSquareBar } from 'react-icons/hi';
import { RiShoppingBag4Line } from 'react-icons/ri';
import { GoContainer } from "react-icons/go";
import { IoPeopleOutline } from 'react-icons/io5';
import LaptopImg from '../assets/editing-laptop-2048px-231551-2x1-1.webp';

import { DashboardCardProps } from "../types/dashboard";
import SideBar from "../layouts/SideBar";
import { Header } from "../layouts/Header";
import { Line, Pie } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, ArcElement, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, ArcElement, Tooltip, Legend);

export const Dashboard = () => {
  const [Active, setActive] = useState<number | null>(0);

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

  // Data for the line chart
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

  // Data for the pie chart
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

        <h1>Welcome Back, Wahab</h1>
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
              <p>View All</p>
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
              <span className="Dashboard_Order_Item">
                <div className="Dashboard_Order_Item_Description">
                  <span className="Item_Img_Holder">
                    <img src={LaptopImg} alt="a laptop" />
                  </span>
                  <span>
                    <h2>HP EliteBook 830 Touchscreen</h2>
                    <h4>Computing</h4>
                  </span>
                </div>
                <div>
                  <p>8976TY</p>
                  <p>$30</p>
                  <p>5,951</p>
                  <p>Delivered</p>
                </div>
              </span>
            </article>

            {/* The new line chart for total sales */}
            <Line data={salesData} options={options} />
          </div>
          <div className="Side_Graph_Container">
            {/* The new pie chart */}
            <Pie data={pieData} />
          </div>
        </section>

        <section className="Bottom_Graph_Container"></section>
      </div>
    </>
  );
};
