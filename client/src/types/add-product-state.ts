export interface ProductFormStateProps {
    img: File | null;
    productName: string;
    productDescription: string;
    productPrice: string;
    currency: string;
    category: string;
    quantity: string;
    errors: {
      productName: string;
      productDescription: string;
      productPrice: string;
      quantity: string;
    };
  }