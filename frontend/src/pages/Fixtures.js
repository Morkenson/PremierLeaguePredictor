import React from 'react';
import styled from 'styled-components';

const ComponentContainer = styled.div`
  padding: 20px;
  text-align: center;
`;

const Title = styled.h2`
  color: #00D4AA;
  margin-bottom: 20px;
  font-size: 28px;
`;

const Message = styled.p`
  color: #A0AEC0;
  font-size: 16px;
`;

const Fixtures = () => {
  return (
    <ComponentContainer>
      <Title>Upcoming Fixtures</Title>
      <Message>Match fixtures and AI predictions coming soon...</Message>
      <Message>Predictions will be generated in real-time!</Message>
    </ComponentContainer>
  );
};

export default Fixtures;