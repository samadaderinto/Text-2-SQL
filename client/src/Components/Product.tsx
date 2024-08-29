import { useReducer, useEffect, Key } from 'react';
import { IoIosAddCircleOutline } from 'react-icons/io';
import { MdOutlineCalendarToday, MdOutlineDelete, MdOutlineEdit } from 'react-icons/md';
import { FiSearch } from 'react-icons/fi';
import { Header } from '../layouts/Header';
import Sidebar from '../layouts/SideBar';
import { useNavigate } from 'react-router-dom';
import ReactPaginate from 'react-paginate';
import api from '../utils/api';

const initialState = {
  currentPage: 0,
  input: '',
  data: [],
  totalPages: 0,
};

function reducer(state: any, action: { type: string; payload: any; }) {
  switch (action.type) {
    case 'SET_CURRENT_PAGE':
      return { ...state, currentPage: action.payload };
    case 'SET_INPUT':
      return { ...state, input: action.payload };
    case 'SET_DATA':
      return { ...state, data: action.payload };
    case 'SET_TOTAL_PAGES':
      return { ...state, totalPages: action.payload };
    default:
      return state;
  }
}

export const Product = () => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const { currentPage, input, data, totalPages } = state;
  const itemsPerPage = 15;
  const navigate = useNavigate();

  useEffect(() => {
    fetchData(currentPage, input);
  }, [currentPage, input]);

  const fetchData = (page: number, query: string) => {
    const offset = page * itemsPerPage;
    api.get(`/product/search/?offset=${offset}&limit=${itemsPerPage}&query=${query}`)
      .then(response => {
        const totalItems = response.data.count || 0;
        dispatch({ type: 'SET_DATA', payload: response.data.products || [] });
        dispatch({ type: 'SET_TOTAL_PAGES', payload: Math.ceil(totalItems / itemsPerPage) });
      })
      .catch(error => {
        console.error("Error fetching data", error);
        dispatch({ type: 'SET_TOTAL_PAGES', payload: 1 });  // Fallback to 1 page in case of an error
      });
  };

  const handlePageClick = (event: { selected: number }) => {
    dispatch({ type: 'SET_CURRENT_PAGE', payload: event.selected });
  };

  const handleEdit = (id: number) => {
    navigate(`/product/edit/${id}`);
  };

  const handleDelete = async (id: number) => {
    if (window.confirm("Are you sure you want to delete this product?")) {
      try {
        await api.delete(`/product/${id}/`);
        dispatch({ type: 'SET_DATA', payload: data.filter((item: any) => item.id !== id) });
      } catch (error) {
        console.error("Error deleting product", error);
      }
    }
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
              onChange={(e) => dispatch({ type: 'SET_INPUT', payload: e.target.value })}
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
          {data.length === 0 ? (
            <div className="No-Product">No Items Found!</div>
          ) : (
            data.map((item: {
              id: number, image: string; available: number, title: string; category: string; status: string; price: string; sold: string; sales: number
            }, index: Key) => (
              <nav key={index}>
                <input type="checkbox" />
                <p className="Product_Name">{item.title}</p>
                <p className='Product_Category'>{item.category}</p>
                <p>{item.available > 0 ? "Available" : "Sold Out"}</p>
                <p>${item.price}</p>
                <p>{item.sales}</p>
                <p>${item.sales * parseInt(item.price)}</p>
                <p className="Product_Icons">
                  <MdOutlineEdit onClick={() => handleEdit(item.id)} />
                  <MdOutlineDelete onClick={() => handleDelete(item.id)} />
                </p>
              </nav>
            ))
          )}

          {totalPages > 1 && (
            <ReactPaginate
              previousLabel={'<'}
              nextLabel={'>'}
              breakLabel={'...'}
              pageCount={totalPages}
              marginPagesDisplayed={2}
              pageRangeDisplayed={5}
              onPageChange={handlePageClick}
              containerClassName={'Product_pagination'}
              activeClassName={'Product_page_active'}
              previousClassName={totalPages === 1 ? 'disabled' : ''}
              nextClassName={totalPages === 1 ? 'disabled' : ''}
              disabledClassName={'pagination_disabled'}
            />
          )}
        </div>
      </section>
    </div>
  );
};
