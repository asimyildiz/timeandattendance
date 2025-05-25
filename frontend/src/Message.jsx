import React from 'react';

const Message = ({ message }) => {
    return (
        <div
            className="prose max-w-none"
            dangerouslySetInnerHTML={{ __html: message }}
        />
    );
};

export default Message;