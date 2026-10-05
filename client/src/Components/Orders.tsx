import { useEffect, useState } from "react";
import { FaAngleLeft, FaAngleRight } from "react-icons/fa";
import { HiMiniMagnifyingGlass } from "react-icons/hi2";
import { MdOutlineDelete, MdOutlineDownload } from "react-icons/md";
import ReactPaginate from 'react-paginate';
import { Header } from "../layouts/Header";
import Sidebar from "../layouts/Sidebar";
import api from "../utils/api";
import { notifyApiError } from "../utils/api-errors";
import { LoadingState } from './LoadingState';
import { waitForQueueJob } from '../utils/queue-jobs';
import { EmptyState } from './EmptyState';

export const Orders = () => {
  const itemsPerPage = 15;

  const [state, setState] = useState({
    input: '',
    currentPage: 0,
    data: [],
    totalItems: 0,
    filter: '',
    isLoading: false,
  });

  useEffect(() => {
    fetchData();
  }, [state.currentPage, state.input, state.filter]);

  const fetchData = async () => {
    const offset = state.currentPage * itemsPerPage;
    setState((prevState) => ({ ...prevState, isLoading: true }));
    try {
      const response = await api.get(`/orders/search/?offset=${offset}&limit=${itemsPerPage}&query=${encodeURIComponent(state.input)}&status=${encodeURIComponent(state.filter)}`);
      setState((prevState) => ({
        ...prevState,
        data: response.data.orders,
        totalItems: response.data.count,
        isLoading: false,
      }));
    } catch (error) {
      notifyApiError(error, "Could not load orders. Please try again.");
      setState((prevState) => ({ ...prevState, isLoading: false }));
    }
  };

  const handlePageClick = (event: { selected: number }) => {
    setState((prevState) => ({
      ...prevState,
      currentPage: event.selected
    }));
  };

  const handleDownload = async (order_id = "") => {
    try {
      const end_point = order_id ? `/orders/download/${order_id}/` : "/orders/download/";
      const queued = await api.get(end_point);
      await waitForQueueJob(queued.data.job_id);
      const response = await api.get(`/jobs/${queued.data.job_id}/download/`, {
        responseType: 'blob',
      });
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', order_id ? `order_${order_id}.csv` : 'orders.csv');
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      notifyApiError(error, "Could not download the order file. Please try again.");
    }
  };

  const handleDelete = async (order_id: any) => {
    try {
      const response = await api.delete(`/orders/delete/${order_id}/`);
      if (response.status === 205) {
        setState((prevState) => ({
          ...prevState,
          data: prevState.data.filter((item: any) => item.id !== order_id),
          totalItems: prevState.totalItems - 1
        }));
      }
    } catch (error) {
      notifyApiError(error, "Could not delete this order. Please try again.");
    }
  };

  const handleFilterChange = (status: string) => {
    setState((prevState) => ({
      ...prevState,
      filter: status,
      currentPage: 0
    }));
  };

  const pageCount = Math.ceil(state.totalItems / itemsPerPage);

  return (
    <>
      <Header />
      <div className="Order_Container">
        <Sidebar />
        <section className="Order_Header">
          <div><small className="Page_Eyebrow">SALES</small><h1>Orders</h1><p>Track purchases and fulfillment activity.</p></div>
          <button type="button" onClick={() => handleDownload()}>
            <MdOutlineDownload className="Order_Download_Icon" />
            Export orders
          </button>
        </section>
        <section className="Order_List_Container">
          <ul>
            {['', 'pending', 'paid', 'cancelled'].map(status => (
              <li key={status}><button type="button" className="Order_Filter_Button" aria-pressed={state.filter === status} onClick={() => handleFilterChange(status)}>{status ? status.charAt(0).toUpperCase() + status.slice(1) : 'All orders'}</button></li>
            ))}
          </ul>
          <div className="Order_Search_Box">
            <HiMiniMagnifyingGlass />
            <input
              type="text"
              aria-label="Search orders"
              value={state.input}
              onChange={(e) => setState((prevState) => ({ ...prevState, input: e.target.value }))}
              placeholder="Search by order or customer"
            />
          </div>

          <div className="Order_List_Header">
            <article>
              <input type="checkbox" />
              <p>Order ID</p>
              <p className='Header_customer_Name'>Customer Name</p>
            </article>
            <div className="Order_Attributes">
              <p>Status</p>
              <p>Date & Time</p>
              <p>Price</p>
              <p>Action</p>
            </div>
          </div>

          <div className="Order_List_Item">
            {state.isLoading ? (
              <LoadingState label="Loading orders" />
            ) : state.data.length === 0 ? (
              <EmptyState title="No orders found" description="New orders and matching search results will appear here." />
            ) : (
              <>
                {state.data.map((orderItem: any, index: number) => (
                  <article key={index}>
                    <input type="checkbox" />
                    <p style={{ color: 'black' }}>{orderItem.id}</p>
                    <p style={{ color: 'black' }}>{orderItem.name}</p>
                    <p className={`Order_Status ${orderItem.status}`}>{orderItem.status}</p>
                    <p>{orderItem.created.substring(0, 10)}</p>
                    <p>{orderItem.subtotal}</p>
                    <div className="Row_Actions">
                      <button type="button" aria-label={`Download order ${orderItem.id}`} onClick={() => handleDownload(orderItem.id)}><MdOutlineDownload /></button>
                      <button type="button" className="danger" aria-label={`Delete order ${orderItem.id}`} onClick={() => handleDelete(orderItem.id)}><MdOutlineDelete /></button>
                    </div>
                  </article>
                ))}

                {pageCount > 1 && (
                  <ReactPaginate
                    previousLabel={<FaAngleLeft className="order_arrow" />}
                    nextLabel={<FaAngleRight className="order_arrow" />}
                    breakLabel={'...'}
                    pageCount={pageCount}
                    marginPagesDisplayed={1}
                    pageRangeDisplayed={3}
                    onPageChange={handlePageClick}
                    containerClassName={'Order_pagination'}
                    activeClassName={'Order_page_active'}
                    previousClassName={pageCount === 1 ? 'disabled' : ''}
                    nextClassName={pageCount === 1 ? 'disabled' : ''}
                    disabledClassName={'pagination_disabled'}
                  />
                )}
              </>
            )}
          </div>
        </section>
      </div>
    </>
  );
};
