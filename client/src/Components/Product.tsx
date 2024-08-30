import { useReducer, useEffect, Key } from 'react';
import { IoIosAddCircleOutline } from 'react-icons/io';
import { FaAngleLeft, FaAngleRight } from "react-icons/fa";
import { MdOutlineCalendarToday, MdOutlineDelete, MdOutlineEdit } from 'react-icons/md';
import { FiSearch } from 'react-icons/fi';
import { Header } from '../layouts/Header';
import Sidebar from '../layouts/SideBar';
import { useNavigate } from 'react-router-dom';
import ReactPaginate from 'react-paginate';
import api from '../utils/api';
import { ClipLoader } from 'react-spinners';

const initialState = {
  currentPage: 1,
  input: '',
  data: [],
  totalPages: 0,
  editingId: null, // State for tracking which product is being edited
  editValues: { title: '', description: '', price: '', category: '', currency: '' }, // State for edit form values
  loading: false, // Add loading state
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
    case 'SET_EDITING_ID':
      return { ...state, editingId: action.payload };
    case 'SET_EDIT_VALUES':
      return { ...state, editValues: { ...state.editValues, ...action.payload } };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    default:
      return state;
  }
}

export const Product = () => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const { currentPage, input, data, totalPages, editingId, editValues, loading } = state;
  const itemsPerPage = 15;
  const navigate = useNavigate();

  useEffect(() => {
    fetchData(currentPage, input);
  }, [currentPage, input]);

  const fetchData = (page: number, query: string) => {
    dispatch({ type: 'SET_LOADING', payload: true }); // Show loading spinner
    const offset = page;
    api.get(`/product/search/?offset=${offset}&limit=${itemsPerPage}&query=${query}`)
      .then(response => {
        const totalItems = response.data.count;
        dispatch({ type: 'SET_DATA', payload: response.data.products });
        dispatch({ type: 'SET_TOTAL_PAGES', payload: Math.ceil(totalItems / itemsPerPage) });
        dispatch({ type: 'SET_LOADING', payload: false }); // Hide loading spinner
      })
      .catch(error => {
        console.error("Error fetching data", error);
        dispatch({ type: 'SET_LOADING', payload: false }); // Hide loading spinner
        dispatch({ type: 'SET_TOTAL_PAGES', payload: 1 });
      });
  };

  const handlePageClick = (event: { selected: number }) => {
    dispatch({ type: 'SET_CURRENT_PAGE', payload: event.selected + 1 }); // Convert 0-based index to 1-based
  };

  const handleEditClick = (item: any) => {
    // Set the product to be edited and populate the edit form values
    dispatch({ type: 'SET_EDITING_ID', payload: item.id });
    dispatch({
      type: 'SET_EDIT_VALUES',
      payload: {
        title: item.title,
        description: item.description,
        price: item.price,
        category: item.category,
        currency: item.currency
      }
    });
  };

  const handleEditChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    dispatch({ type: 'SET_EDIT_VALUES', payload: { [e.target.name]: e.target.value } });
  };

  const handleEditSubmit = () => {
    api.put(`/product/update/`, {
      id: editingId, // Pass the product ID to identify which product to update
      ...editValues
    })
      .then(response => {
        // Update the product in the data list with the new values
        const updatedData = data.map((item: any) =>
          item.id === editingId ? { ...item, ...editValues } : item
        );
        dispatch({ type: 'SET_DATA', payload: updatedData });
        dispatch({ type: 'SET_EDITING_ID', payload: null }); // Exit edit mode
      })
      .catch(error => {
        console.error("Error updating product", error);
      });
  };

  const handleDelete = async (id: number) => {
    try {
      await api.delete(`/product/delete/${id}/`);
      dispatch({ type: 'SET_DATA', payload: data.filter((item: any) => item.id !== id) });
    } catch (error) {
      console.error("Error deleting product", error);
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
          {loading ? (
            <div className="spinner-container">
              <ClipLoader color="#36d7b7" loading={loading} size={50} />
            </div>
          ) : (
            <>
              {data.length === 0 ? (
                <div className="No-Product">No Items Found!</div>
              ) : (
                data.map((item: any, index: Key) => (
                  <nav key={index}>
                    <input type="checkbox" />
                    {editingId === item.id ? (
                      <>
                        <input
                          type="text"
                          name="title"
                          value={editValues.title}
                          onChange={handleEditChange}
                          placeholder="Product Name"
                        />
                        <input
                          type="text"
                          name="category"
                          value={editValues.category}
                          onChange={handleEditChange}
                          placeholder="Category"
                        />
                        <input
                          type="text"
                          name="price"
                          value={editValues.price}
                          onChange={handleEditChange}
                          placeholder="Price"
                        />
                        <button onClick={handleEditSubmit}>Save</button>
                      </>
                    ) : (
                      <>
                        <p className="Product_Name">{item.title}</p>
                        <p className="Product_Category">{item.category}</p>
                        <p>{item.available > 0 ? "Available" : "Sold Out"}</p>
                        <p>${item.price}</p>
                        <p>{item.sales}</p>
                        <p>${item.sales * parseInt(item.price)}</p>
                        <p className="Product_Icons">
                          <MdOutlineEdit onClick={() => handleEditClick(item)} />
                          <MdOutlineDelete onClick={() => handleDelete(item.id)} />
                        </p>
                      </>
                    )}
                  </nav>
                ))
              )}
              {totalPages > 1 && (
                <ReactPaginate
                  previousLabel={<FaAngleLeft className="order_arrow" />}
                  nextLabel={<FaAngleRight className="order_arrow" />}
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
            </>
          )}
        </div>
      </section>
    </div>
  );
};


