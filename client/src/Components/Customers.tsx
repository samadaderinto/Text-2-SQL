import { useEffect, useState } from "react";
import { FaAngleLeft, FaAngleRight } from "react-icons/fa";
import { FiSearch } from "react-icons/fi";
import { IoIosAddCircleOutline } from "react-icons/io";
import ReactPaginate from "react-paginate";
import { useNavigate } from "react-router-dom";
import { Header } from "../layouts/Header";
import Sidebar from '../layouts/Sidebar';
import { CustomerProps } from "../types/customers";
import api from "../utils/api";
import { notifyApiError } from "../utils/api-errors";
import { LoadingState } from "./LoadingState";
import { EmptyState } from "./EmptyState";

export const Customers = () => {
  const itemsPerPage = 15;
  const [data, setData] = useState<CustomerProps[]>([]);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [totalItems, setTotalItems] = useState(0);
  const nav = useNavigate();

  const fetchData = async () => {
    setLoading(true);
    try {
      const response = await api.get(`/customers/search/?offset=${currentPage}&limit=${itemsPerPage}&query=${encodeURIComponent(searchQuery)}`);
      setData(response.data.customers ?? []);
      setTotalItems(response.data.count ?? 0);
    } catch (error) {
      notifyApiError(error, "Could not load customers. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [currentPage, searchQuery]);

  const handlePageClick = (event: { selected: number }) => {
    setCurrentPage(event.selected + 1);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setCurrentPage(1);
  };

  // Calculate the total number of pages
  const totalPages = Math.ceil(totalItems / itemsPerPage);

  return (
    <>
      <Header />
      <Sidebar />


      <div className="Customer_Container">

        <article>
          
          <div><small className="Page_Eyebrow">AUDIENCE</small><h1>Customers</h1><p>View and manage your customer directory.</p></div>
          <button type="button" onClick={() => nav('/customers/add')}>
            <IoIosAddCircleOutline className="Circle_Icon" /> Add customer
          </button>
        </article>

        <section className="Customer_List_Container">
          <article>
            <div>
              <FiSearch />
              <input
                className="Search_Icon_Input"
                type="text"
                aria-label="Search customers"
                placeholder="Search Name"
                value={searchQuery}
                onChange={handleSearchChange}
              />
            </div>
          </article>

          <article className="Customer_List_Header">
            <div>
              <input type="checkbox" />
              <p>ID</p>
              <p>Customer Name</p>
            </div>
            <p>Email</p>
            <div>
              <p className="Date_Joined">Date Joined</p>
            </div>
          </article>

          <section className="Customer_List">
            {loading ? (
              <LoadingState label="Loading customers" />
            ) : data.length === 0 ? (
              <EmptyState title="No customers yet" description="Add your first customer to begin your directory." />
            ) : (
              data.map((item) => (
                <article key={item.id}>
                  <span>
                    <input type="checkbox" />
                    <p className="Id_customer">{item.id}</p>
                    <p className="Customer_Name">{item.last_name} {item.first_name}</p>
                  </span>
                  <p>{item.email}</p>
                  <span>
                    <p className="Date_Joined">{item.created.substring(0, 10)}</p>
                  </span>
                </article>
              ))
            )}

            {totalPages > 1 && !loading && (
              <ReactPaginate
                previousLabel={<FaAngleLeft className="customer_arrow" />}
                nextLabel={<FaAngleRight className="customer_arrow" />}
                breakLabel={'...'}
                pageCount={totalPages}
                marginPagesDisplayed={2}
                pageRangeDisplayed={5}
                onPageChange={handlePageClick}
                containerClassName={'Customer_pagination'}
                activeClassName={'Order_page_active'}
              />
            )}
          </section>
        </section>
      </div>
    </>
  );
};
