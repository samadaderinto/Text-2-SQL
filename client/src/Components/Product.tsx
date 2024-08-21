import { useState, useEffect } from 'react';
import { IoIosAddCircleOutline } from 'react-icons/io';
import { MdOutlineCalendarToday, MdOutlineDelete, MdOutlineEdit } from 'react-icons/md';
import { FiSearch } from 'react-icons/fi';
import { Header } from '../layouts/Header';
import Sidebar from '../layouts/SideBar';
import { useNavigate } from 'react-router-dom';
import ReactPaginate from 'react-paginate';
import axios from 'axios';
import { API_BASE_URL } from '../utils/api';

export const Product = () => {
  const [currentPage, setCurrentPage] = useState(0);
  const itemsPerPage = 15;
  const [input, setInput] = useState('');
  const [data, setData] = useState<any[]>([]);
  const [totalPages, setTotalPages] = useState(0);

  const offset = currentPage * itemsPerPage;
  const access = localStorage.getItem('access');
  const navigate = useNavigate();

  // Fetch data when currentPage or input changes
  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = await axios.get(
          `${API_BASE_URL}/products/search/?offset=${offset}&limit=${itemsPerPage}&query=${input}`, 
          {
            headers: {
              Authorization: `Bearer ${access}`,
            },
          }
        );
        setData(response.data.items || []); // Adjust based on your API response
        setTotalPages(Math.ceil(response.data.totalCount / itemsPerPage)); // Adjust based on your API response
      } catch (error) {
        console.error("Error fetching data", error);
      }
    };

    fetchData();
  }, [currentPage, input]);

  const handlePageClick = (event: { selected: number }) => {
    setCurrentPage(event.selected);
  };

  return (
    <div className="Product_Container">
      <Header />
      <Sidebar />
      <section className="Add_Product">
        <h1>All Products</h1>
        <span onClick={() => navigate('/product/add')}>
          <IoIosAddCircleOutline className="Product_Icon" />
          Add new Product
        </span>
      </section>
      <section className="Product_Table_Section">
        <div>
          <span>
            <FiSearch className="Search_Icon" />
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Search Name"
            />
          </span>
          <MdOutlineCalendarToday />
        </div>
        <div className="Product_Table_list_header">
          <span>
            <input type="checkbox" />
            <p>Product Name</p>
          </span>
          <ul>
            <li>Category</li>
            <li>Status</li>
            <li>Price</li>
            <li>Sold</li>
            <li>Sales</li>
          </ul>
          <p>Action</p>
        </div>
        <div className="Product_Table_List_content">
          {data.map((item, index) => (
            <nav key={index}>
              <span>
                <input type="checkbox" />
                <article className="Product_Img_Container">
                  <img src={item.imageUrl || ''} alt={item.name || 'Product Image'} />
                </article>
                <p>{item.name || 'Product Name'}</p>
              </span>
              <span className="Product_Details">
                <p className="Product_Category">{item.category || 'Category'}</p>
                <p className="Product_Available">{item.status || 'Status'}</p>
                <p>${item.price || '0.00'}</p>
                <p>{item.sold || '0'}</p>
                <p>${item.sales || '0.00'}</p>
              </span>
              <p className="Product_Icons">
                <MdOutlineEdit />
                <MdOutlineDelete />
              </p>
            </nav>
          ))}

          <ReactPaginate
            previousLabel={'previous'}
            nextLabel={'next'}
            breakLabel={'...'}
            pageCount={totalPages}
            marginPagesDisplayed={2}
            pageRangeDisplayed={5}
            onPageChange={handlePageClick}
            containerClassName={'Order_pagination'}
            activeClassName={'Order_page_active'}
          />
        </div>
      </section>
    </div>
  );
};
