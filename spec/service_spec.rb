require_relative '../service'


describe Service do
  describe :initialize do
    it 'should initialize general purpose input/output' do
      expect(GPIO).to receive :new
      Service.new
    end
  end
end
