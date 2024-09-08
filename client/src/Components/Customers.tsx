import { useEffect, useState } from "react";
import { FaAngleLeft, FaAngleRight } from "react-icons/fa";
import { FiSearch } from "react-icons/fi";
import { IoIosAddCircleOutline } from "react-icons/io";
import { MdOutlineCalendarToday, MdOutlineDelete, MdOutlineEdit } from "react-icons/md";
import ReactPaginate from "react-paginate";
import { useNavigate } from "react-router-dom";
import { Header } from "../layouts/Header";
import Sidebar from '../layouts/SideBar';
import { CustomerProps } from "../types/customers";
import api from "../utils/api";
import { ClipLoader } from "react-spinners";

export const Customers = () => {
  const itemsPerPage = 15;
  const [data, setData] = useState<CustomerProps[]>([]);
  const [currentPage, setCurrentPage] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const nav = useNavigate();

  const fetchData = async () => {
    const offset = currentPage * itemsPerPage;
    setLoading(true);
    try {
      const response = await api.get(`/customers/search/?offset=${offset}&limit=${itemsPerPage}&query=${searchQuery}`);
      setData(response.data.customers);
    } catch (error) {
      console.error("Error fetching data", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, [currentPage, searchQuery]);

  const handlePageClick = (event: { selected: number }) => {
    setCurrentPage(event.selected);
  };

  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSearchQuery(e.target.value);
    setCurrentPage(0);
  };

  // Calculate the total number of pages
  const totalPages = Math.ceil(data.length / itemsPerPage);

  return (
    <>
      <Header />
      <Sidebar />


      <div className="Customer_Container">

        <article>
          
          <h1>Customers</h1>
          <span onClick={() => nav('/customers/add')}>
            <IoIosAddCircleOutline className="Circle_Icon" /> Add New Customers
          </span>
        </article>

        <section className="Customer_List_Container">
          <article>
            <div>
              <FiSearch />
              <input
                className="Search_Icon_Input"
                type="text"
                placeholder="Search Name"
                value={searchQuery}
                onChange={handleSearchChange}
              />
            </div>
            <MdOutlineCalendarToday className="Customer_Calendar" />
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
            <p>Action</p>
          </article>

          <section className="Customer_List">
            {loading ? (
              <div className="loading-spinner">
                <ClipLoader size={50} color={"#123abc"} loading={loading} />
              </div>
            ) : (
              data.map((item) => (
                <article key={item.id}>
                  <span>
                    <input type="checkbox" />
                    <p className="Id_customer">{item.id}</p>
                    <div>
                      <img src="" alt="" />
                    </div>
                    <p className="Customer_Name">{item.first_name}</p>
                  </span>
                  <p>{item.email}</p>
                  <span>
                    <p className="Date_Joined">{item.created.substring(0, 10)}</p>
                  </span>
                  <p className="Customer_Action_Icon">
                    <MdOutlineEdit />
                    <MdOutlineDelete />
                  </p>
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
