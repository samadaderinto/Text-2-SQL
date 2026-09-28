import { useContext, useEffect, useMemo, useState } from "react";
import { GoContainer } from "react-icons/go";
import { HiOutlineChartSquareBar } from "react-icons/hi";
import { IoPeopleOutline } from "react-icons/io5";
import { RiShoppingBag4Line } from "react-icons/ri";
import {
  ArcElement,
  CategoryScale,
  Chart as ChartJS,
  Legend,
  LinearScale,
  LineElement,
  PointElement,
  Tooltip,
} from "chart.js";
import { Doughnut, Line } from "react-chartjs-2";
import { Link, useNavigate } from "react-router-dom";
import { AuthContext } from "../contexts/auth-context";
import { Header } from "../layouts/Header";
import Sidebar from "../layouts/Sidebar";
import { OrderProps } from "../types/order";
import api from "../utils/api";
import { Oval } from "react-loader-spinner";

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  ArcElement,
  Tooltip,
  Legend,
);

const formatCurrency = (value: string | number) => {
  const amount = Number(value);
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
  }).format(Number.isFinite(amount) ? amount : 0);
};

export const Dashboard = () => {
  const { isSignedIn, user } = useContext(AuthContext);
  const [orders, setOrders] = useState<OrderProps[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const nav = useNavigate();

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        const response = await api.get("/orders/search/?limit=5");
        setOrders(response.data.orders ?? []);
      } catch {
        setError("We couldn't load your latest orders. Please refresh to try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, []);

  const paidOrders = useMemo(
    () => orders.filter((order) => order.status.toLowerCase() === "paid"),
    [orders],
  );
  const pendingOrders = useMemo(
    () => orders.filter((order) => order.status.toLowerCase() === "pending"),
    [orders],
  );
  const recentRevenue = useMemo(
    () =>
      orders.reduce((total, order) => {
        const amount = Number(order.subtotal);
        return total + (Number.isFinite(amount) ? amount : 0);
      }, 0),
    [orders],
  );

  const metrics = [
    {
      icon: <HiOutlineChartSquareBar />,
      label: "Recent orders",
      value: loading ? "—" : String(orders.length),
      detail: "Latest five orders",
      tone: "violet",
    },
    {
      icon: <RiShoppingBag4Line />,
      label: "Paid",
      value: loading ? "—" : String(paidOrders.length),
      detail: "In your latest five",
      tone: "green",
    },
    {
      icon: <GoContainer />,
      label: "Awaiting payment",
      value: loading ? "—" : String(pendingOrders.length),
      detail: "In your latest five",
      tone: "amber",
    },
    {
      icon: <IoPeopleOutline />,
      label: "Recent order value",
      value: loading ? "—" : formatCurrency(recentRevenue),
      detail: "Subtotal of latest five",
      tone: "blue",
    },
  ];

  const statusData = {
    labels: ["Paid", "Pending", "Cancelled"],
    datasets: [
      {
        data: [
          paidOrders.length,
          pendingOrders.length,
          orders.filter((order) => order.status.toLowerCase() === "cancelled")
            .length,
        ],
        backgroundColor: ["#20a779", "#f3a541", "#e46e78"],
        borderWidth: 0,
        hoverOffset: 5,
      },
    ],
  };

  const revenueData = {
    labels: orders.map((order) => `#${order.id.slice(-5)}`),
    datasets: [
      {
        label: "Order subtotal",
        data: orders.map((order) => {
          const amount = Number(order.subtotal);
          return Number.isFinite(amount) ? amount : 0;
        }),
        borderColor: "#6259e8",
        backgroundColor: "rgba(98, 89, 232, 0.10)",
        borderWidth: 2.5,
        pointRadius: 4,
        pointHoverRadius: 6,
        pointBackgroundColor: "#fff",
        pointBorderColor: "#6259e8",
        pointBorderWidth: 2,
        fill: true,
        tension: 0.38,
      },
    ],
  };

  const userName = user?.email?.split("@")[0] || "there";

  return (
    <>
      <Header />
      <div className="Dashboard_container">
        <Sidebar />

        <main className="Dashboard_Content">
          <section className="Dashboard_Intro">
            <div>
              <span className="Dashboard_Eyebrow">YOUR BUSINESS, IN FOCUS</span>
              <h1>
                {isSignedIn ? `Good to see you, ${userName}` : "Your store at a glance"}
              </h1>
              <p>A clear view of what’s happening across your store.</p>
            </div>
            <button
              className="Dashboard_Query_Button"
              onClick={() => nav("/query")}
              type="button"
            >
              <HiOutlineChartSquareBar aria-hidden="true" />
              Ask your data
            </button>
          </section>

          <section className="Dashboard_Card_Container" aria-label="Recent order summary">
            {metrics.map((metric) => (
              <article key={metric.label} className={`Dashboard_Metric ${metric.tone}`}>
                <div className="Dashboard_Metric_Top">
                  <span className="Dashboard_Metric_Icon">{metric.icon}</span>
                  <span className="Dashboard_Metric_Label">{metric.label}</span>
                </div>
                <h2>{metric.value}</h2>
                <p>{metric.detail}</p>
              </article>
            ))}
          </section>

          <section className="Dashboard_Analytics">
            <article className="Dashboard_Panel Dashboard_Revenue_Panel">
              <header className="Dashboard_Panel_Header">
                <div>
                  <span className="Dashboard_Eyebrow">ORDER ACTIVITY</span>
                  <h2>Recent order value</h2>
                </div>
                <Link to="/orders">All orders <span aria-hidden="true">↗</span></Link>
              </header>
              {loading ? (
                <div className="Dashboard_Chart_State">
                  <Oval height={34} width={34} color="#6259e8" ariaLabel="Loading orders" />
                </div>
              ) : error ? (
                <p className="Dashboard_Chart_State Dashboard_Error">{error}</p>
              ) : orders.length === 0 ? (
                <div className="Dashboard_Chart_State">
                  <span>No orders yet</span>
                  <p>Your recent order activity will show up here.</p>
                </div>
              ) : (
                <div className="Dashboard_Line_Chart">
                  <Line
                    data={revenueData}
                    options={{
                      maintainAspectRatio: false,
                      plugins: { legend: { display: false } },
                      scales: {
                        x: { grid: { display: false }, border: { display: false } },
                        y: {
                          beginAtZero: true,
                          grid: { color: "#f0f1f7" },
                          border: { display: false, dash: [4, 4] },
                          ticks: { maxTicksLimit: 5 },
                        },
                      },
                    }}
                  />
                </div>
              )}
              <p className="Dashboard_Chart_Footnote">Based on your latest five orders</p>
            </article>

            <article className="Dashboard_Panel Dashboard_Status_Panel">
              <header className="Dashboard_Panel_Header">
                <div>
                  <span className="Dashboard_Eyebrow">AT A GLANCE</span>
                  <h2>Order status</h2>
                </div>
                <span className="Dashboard_Sample_Label">LATEST 5</span>
              </header>
              {loading ? (
                <div className="Dashboard_Chart_State">
                  <Oval height={34} width={34} color="#6259e8" ariaLabel="Loading order status" />
                </div>
              ) : error ? (
                <p className="Dashboard_Chart_State Dashboard_Error">{error}</p>
              ) : orders.length === 0 ? (
                <div className="Dashboard_Chart_State">
                  <span>Nothing to chart yet</span>
                  <p>Order statuses will appear here.</p>
                </div>
              ) : (
                <>
                  <div className="Dashboard_Doughnut">
                    <Doughnut
                      data={statusData}
                      options={{
                        cutout: "76%",
                        plugins: { legend: { display: false } },
                        maintainAspectRatio: false,
                      }}
                    />
                    <div className="Dashboard_Doughnut_Center">
                      <strong>{orders.length}</strong>
                      <span>orders</span>
                    </div>
                  </div>
                  <ul className="Dashboard_Status_Legend">
                    <li><span className="paid-dot" />Paid <strong>{paidOrders.length}</strong></li>
                    <li><span className="pending-dot" />Pending <strong>{pendingOrders.length}</strong></li>
                    <li>
                      <span className="cancelled-dot" />Cancelled
                      <strong>{statusData.datasets[0].data[2]}</strong>
                    </li>
                  </ul>
                </>
              )}
            </article>
          </section>

          <section className="Dashboard_Panel Dashboard_Orders_Panel">
            <header className="Dashboard_Panel_Header">
              <div>
                <span className="Dashboard_Eyebrow">THE LATEST</span>
                <h2>Recent orders</h2>
              </div>
              <Link to="/orders">View all orders <span aria-hidden="true">↗</span></Link>
            </header>

            {loading ? (
              <div className="Dashboard_Orders_State">
                <Oval height={36} width={36} color="#6259e8" ariaLabel="Loading orders" />
              </div>
            ) : error ? (
              <p className="Dashboard_Orders_State Dashboard_Error">{error}</p>
            ) : orders.length === 0 ? (
              <div className="Dashboard_Orders_State">
                <span>It’s quiet in here — for now.</span>
                <p>Your new orders will appear here as soon as they come in.</p>
              </div>
            ) : (
              <div className="Dashboard_Table_Wrapper">
                <table className="Dashboard_Table">
                  <thead>
                    <tr>
                      <th>Order</th>
                      <th>Customer</th>
                      <th>Category</th>
                      <th>Status</th>
                      <th className="amount-cell">Subtotal</th>
                    </tr>
                  </thead>
                  <tbody>
                    {orders.map((order) => (
                      <tr key={order.id}>
                        <td className="order-id">#{order.id.slice(-8)}</td>
                        <td>{order.name || "—"}</td>
                        <td>{order.category || "—"}</td>
                        <td>
                          <span className={`Dashboard_Status_Badge ${order.status.toLowerCase()}`}>
                            <span />
                            {order.status}
                          </span>
                        </td>
                        <td className="amount-cell">{formatCurrency(order.subtotal)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        </main>
      </div>
    </>
  );
};
